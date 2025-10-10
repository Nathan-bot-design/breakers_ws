import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
import cv2, numpy as np, base64, json, os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# === Globals ===
bridge = CvBridge()
latest_raw = None
latest_compressed = None
latest_annotated = None
latest_metadata = {}

# === Model Setup ===
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair",
           "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa",
           "train", "tvmonitor"]

def load_detector():
    base = os.path.dirname(__file__)
    return cv2.dnn.readNetFromCaffe(
        os.path.join(base, 'models', 'MobileNetSSD_deploy.prototxt'),
        os.path.join(base, 'models', 'MobileNetSSD_deploy.caffemodel')
    )

DETECTOR = load_detector()

def detect_objects(image, threshold=0.5):
    h, w = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
    DETECTOR.setInput(blob)
    detections = DETECTOR.forward()
    results = []
    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]
        if conf > threshold:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            results.append({
                "label": CLASSES[idx],
                "confidence": float(conf),
                "bbox": box.astype("int").tolist()
            })
    return results

def annotate_image(image, objects):
    for obj in objects:
        x1, y1, x2, y2 = obj["bbox"]
        label = f"{obj['label']}: {obj['confidence']:.2f}"
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

# === ROS Node ===
class ImageStreamNode(Node):
    def __init__(self):
        super().__init__('image_stream_node')
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.pub_original = self.create_publisher(Image, '/image_original', 10)
        self.pub_compressed = self.create_publisher(CompressedImage, '/image_compressed', 10)
        self.pub_annotated = self.create_publisher(Image, '/image_annotated', 10)

    def image_callback(self, msg):
        global latest_raw, latest_compressed, latest_annotated, latest_metadata
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            latest_raw = cv_image
            self.pub_original.publish(msg)

            _, jpeg = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            compressed_msg = CompressedImage()
            compressed_msg.header = msg.header
            compressed_msg.format = 'jpeg'
            compressed_msg.data = jpeg.tobytes()
            self.pub_compressed.publish(compressed_msg)
            latest_compressed = jpeg.tobytes()

            objects = detect_objects(cv_image)
            annotated = annotate_image(cv_image.copy(), objects)
            annotated_msg = bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
            annotated_msg.header = msg.header
            self.pub_annotated.publish(annotated_msg)

            _, annotated_jpeg = cv2.imencode('.jpg', annotated)
            latest_annotated = annotated_jpeg.tobytes()

            latest_metadata = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "objects": objects,
                "num_objects": len(objects)
            }

        except Exception as e:
            self.get_logger().error(f"Image processing failed: {e}")

# === HTTP Server ===
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'surveillance.html')

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global latest_compressed, latest_annotated, latest_raw, latest_metadata
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            def encode(img):
                return base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('utf-8') if img is not None else ''

            def encode_bytes(b):
                return base64.b64encode(b).decode('utf-8') if b else ''

            try:
                with open(TEMPLATE_PATH, 'r') as f:
                    html = f.read()
                html = html.replace('{{timestamp}}', latest_metadata.get('timestamp', 'N/A'))
                html = html.replace('{{original}}', encode(latest_raw))
                html = html.replace('{{compressed}}', encode_bytes(latest_compressed))
                html = html.replace('{{annotated}}', encode_bytes(latest_annotated))
                html = html.replace('{{metadata}}', json.dumps(latest_metadata, indent=2))
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"<h1>Error loading dashboard</h1><pre>{e}</pre>".encode('utf-8'))
        
        elif self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "timestamp": latest_metadata.get("timestamp", "N/A"),
                "compressed": base64.b64encode(latest_compressed).decode('utf-8') if latest_compressed else "",
                "annotated": base64.b64encode(latest_annotated).decode('utf-8') if latest_annotated else "",
                "objects": latest_metadata.get("objects", []),
                "num_objects": latest_metadata.get("num_objects", 0)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    server = HTTPServer(('0.0.0.0', 8080), DashboardHandler)
    print("Dashboard running at http://localhost:8080/")
    server.serve_forever()

# === Entry Point ===
def main(args=None):
    rclpy.init(args=args)
    node = ImageStreamNode()
    Thread(target=start_http_server, daemon=True).start()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
