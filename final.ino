#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

const char* ssid     = "Gautham's S24 Ultra";
const char* password = "gautham@123";

const int BASE_PIN     = 13;
const int SHOULDER_PIN = 12;
const int ARM_PIN      = 14;
const int GRIPPER_PIN  = 27;

WebServer server(80);

Servo baseServo;
Servo shoulderServo;
Servo armServo;
Servo gripperServo;

int    baseAngle     = 90;
int    shoulderAngle = 90;
int    armAngle      = 90;
int    gripperAngle  = 90;
bool   stopped       = false;
String currentMode   = "gesture";

int clamp(int v, int lo, int hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

void addCORSHeaders() {
  server.sendHeader("Access-Control-Allow-Origin",  "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}

void handleOptions() {
  addCORSHeaders();
  server.send(200, "text/plain", "OK");
}

void applyServos() {
  baseServo.write(baseAngle);
  shoulderServo.write(shoulderAngle);
  armServo.write(armAngle);
  gripperServo.write(gripperAngle);
}

void handleRoot() {
  addCORSHeaders();

  String html =
    "<!DOCTYPE html><html><head>"
    "<title>Robot Arm</title>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<style>"
    "body{font-family:Arial;background:#1e1e1e;color:#fff;text-align:center;padding:20px;}"
    "input[type=range]{width:80%;margin:8px 0;}"
    "button{padding:10px 20px;margin:8px;font-size:15px;border:none;border-radius:8px;cursor:pointer;}"
    ".g{background:#22c55e;color:#fff;} .m{background:#2563eb;color:#fff;}"
    ".h{background:#f59e0b;color:#fff;} .s{background:#ef4444;color:#fff;}"
    "label{display:block;margin-top:14px;color:#94a3b8;}"
    "#status{margin:12px;padding:8px;border-radius:8px;background:#0f172a;}"
    "</style></head><body>"
    "<h2>&#129470; ESP32 Robot Arm</h2>"
    "<div id='status'>Mode: <b id='m'>" + currentMode + "</b></div>"
    "<label>Base <span id='bv'>" + String(baseAngle) + "&deg;</span></label>"
    "<input type='range' min='0' max='180' value='" + String(baseAngle) + "' oninput='upd(this,\"bv\")' onchange='send()' id='b'>"
    "<label>Shoulder <span id='sv'>" + String(shoulderAngle) + "&deg;</span></label>"
    "<input type='range' min='0' max='180' value='" + String(shoulderAngle) + "' oninput='upd(this,\"sv\")' onchange='send()' id='s'>"
    "<label>Arm <span id='av'>" + String(armAngle) + "&deg;</span></label>"
    "<input type='range' min='0' max='180' value='" + String(armAngle) + "' oninput='upd(this,\"av\")' onchange='send()' id='a'>"
    "<label>Gripper <span id='gv'>" + String(gripperAngle) + "&deg;</span></label>"
    "<input type='range' min='0' max='180' value='" + String(gripperAngle) + "' oninput='upd(this,\"gv\")' onchange='send()' id='g'>"
    "<br>"
    "<button class='g' onclick='mode(\"gesture\")'>Gesture</button>"
    "<button class='m' onclick='mode(\"manual\")'>Manual</button>"
    "<button class='h' onclick='home()'>Home</button>"
    "<button class='s' onclick='stop()'>Stop</button>"
    R"rawliteral(
<script>
function upd(el,id){ document.getElementById(id).textContent = el.value + '°'; }
function send(){
  fetch('/servo',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({base:+b.value,shoulder:+s.value,arm:+a.value,gripper:+g.value})});
}
function mode(m){
  fetch('/mode',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:m})}).then(()=>{ document.getElementById('m').textContent=m; });
}
function home(){
  b.value=s.value=a.value=g.value=90;
  document.getElementById('bv').textContent='90°';
  document.getElementById('sv').textContent='90°';
  document.getElementById('av').textContent='90°';
  document.getElementById('gv').textContent='90°';
  send();
}
function stop(){ fetch('/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}); }
</script>
)rawliteral"
    "</body></html>";

  server.send(200, "text/html", html);
}

void handleStatus() {
  addCORSHeaders();

  StaticJsonDocument<256> doc;
  doc["mode"]     = currentMode;
  doc["base"]     = baseAngle;
  doc["shoulder"] = shoulderAngle;
  doc["arm"]      = armAngle;
  doc["gripper"]  = gripperAngle;
  doc["stopped"]  = stopped;

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleServo() {
  addCORSHeaders();

  if (stopped) {
    server.send(423, "text/plain", "STOPPED — send mode=manual to resume");
    return;
  }

  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, server.arg("plain"));
  if (err) {
    server.send(400, "text/plain", "Bad JSON");
    return;
  }

  baseAngle     = clamp((int)doc["base"],     0, 180);
  shoulderAngle = clamp((int)doc["shoulder"], 0, 180);
  armAngle      = clamp((int)doc["arm"],      0, 180);
  gripperAngle  = clamp((int)doc["gripper"],  0, 180);

  applyServos();

  server.send(200, "text/plain", "OK");
  Serial.printf("[SERVO] B:%d S:%d A:%d G:%d (mode=%s)\n",
                baseAngle, shoulderAngle, armAngle, gripperAngle,
                currentMode.c_str());
}

void handleGesture() {
  addCORSHeaders();

  if (stopped) {
    server.send(423, "text/plain", "STOPPED");
    return;
  }

  if (currentMode != "gesture") {
    server.send(409, "text/plain", "Not in gesture mode");
    return;
  }

  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, server.arg("plain"));
  if (err) {
    server.send(400, "text/plain", "Bad JSON");
    return;
  }

  String cmd = doc["command"] | "";

  if      (cmd == "BASE_LEFT")      baseAngle     = clamp(baseAngle - 5, 0, 180);
  else if (cmd == "BASE_RIGHT")     baseAngle     = clamp(baseAngle + 5, 0, 180);
  else if (cmd == "SHOULDER_UP")    shoulderAngle = clamp(shoulderAngle + 5, 0, 180);
  else if (cmd == "SHOULDER_DOWN")  shoulderAngle = clamp(shoulderAngle - 5, 0, 180);
  else if (cmd == "ELBOW_UP")       armAngle      = clamp(armAngle + 5, 0, 180);
  else if (cmd == "ELBOW_DOWN")     armAngle      = clamp(armAngle - 5, 0, 180);
  else if (cmd == "GRIP_OPEN")      gripperAngle  = clamp(gripperAngle + 5, 0, 180);
  else if (cmd == "GRIP_CLOSE")     gripperAngle  = clamp(gripperAngle - 5, 0, 180);
  else if (cmd == "STOP") {
    stopped     = true;
    currentMode = "stop";
  } else {
    server.send(400, "text/plain", "Unknown command");
    return;
  }

  applyServos();
  server.send(200, "application/json", "{\"status\":\"ok\"}");
  Serial.printf("[GESTURE] %s -> B:%d S:%d A:%d G:%d\n",
                cmd.c_str(), baseAngle, shoulderAngle, armAngle, gripperAngle);
}

void handleMode() {
  addCORSHeaders();

  StaticJsonDocument<64> doc;
  DeserializationError err = deserializeJson(doc, server.arg("plain"));
  if (err) {
    server.send(400, "text/plain", "Bad JSON");
    return;
  }

  String newMode = doc["mode"].as<String>();

  if (newMode == "gesture" || newMode == "manual") {
    currentMode = newMode;
    stopped     = false;
    server.send(200, "text/plain", "Mode: " + currentMode);
    Serial.println("[MODE] -> " + currentMode);
  } else if (newMode == "stop") {
    stopped     = true;
    currentMode = "stop";
    server.send(200, "text/plain", "Mode: stop");
    Serial.println("[MODE] -> stop");
  } else {
    server.send(400, "text/plain", "Unknown mode. Use: gesture | manual | stop");
  }
}

void handleStop() {
  addCORSHeaders();
  stopped     = true;
  currentMode = "stop";
  server.send(200, "text/plain", "EMERGENCY STOP — all servos frozen");
  Serial.println("[STOP] Emergency stop triggered");
}

void handleNotFound() {
  addCORSHeaders();
  server.send(404, "text/plain", "Not found: " + server.uri());
}

void setup() {
  Serial.begin(115200);

  baseServo.attach(BASE_PIN);
  shoulderServo.attach(SHOULDER_PIN);
  armServo.attach(ARM_PIN);
  gripperServo.attach(GRIPPER_PIN);

  applyServos();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("[WIFI] IP: ");
  Serial.println(WiFi.localIP());

  server.on("/",        HTTP_GET,     handleRoot);
  server.on("/status",  HTTP_GET,     handleStatus);
  server.on("/servo",   HTTP_POST,    handleServo);
  server.on("/gesture", HTTP_POST,    handleGesture);
  server.on("/mode",    HTTP_POST,    handleMode);
  server.on("/stop",    HTTP_POST,    handleStop);

  server.on("/servo",   HTTP_OPTIONS, handleOptions);
  server.on("/gesture", HTTP_OPTIONS, handleOptions);
  server.on("/mode",    HTTP_OPTIONS, handleOptions);
  server.on("/stop",    HTTP_OPTIONS, handleOptions);
  server.on("/status",  HTTP_OPTIONS, handleOptions);

  server.onNotFound(handleNotFound);

  server.begin();
  Serial.printf("[HTTP] http://%s/\n", WiFi.localIP().toString().c_str());
}

void loop() {
  server.handleClient();
}
