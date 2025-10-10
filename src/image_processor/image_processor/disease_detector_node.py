import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2, numpy as np, base64, json, os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from tensorflow import keras
from keras.models import load_model

# === Globals ===
bridge = CvBridge()
latest_raw = None
latest_compressed = None
latest_annotated = None
latest_metadata = {}

# === Model Setup ===
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "potato_disease_model.keras")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "models", "labels.txt")

MODEL = load_model(MODEL_PATH)
with open(LABELS_PATH, "r") as f:
    CLASSES = [line.strip() for line in f.readlines()]


def detect_objects(image):
    input_size = MODEL.input_shape[1:3]
    resized = cv2.resize(image, (input_size[1], input_size[0]))
    normalized = resized.astype("float32") / 255.0
    input_data = np.expand_dims(normalized, axis=0)

    preds = MODEL.predict(input_data)[0]
    idx = int(np.argmax(preds))
    print(preds)
    print(preds[idx])
    confidence = float(preds[idx])

    if confidence < 0.8:
        return [{
            "label": "Processing",
            "confidence": 0.0,
            "bbox": None
        }]
    else:
        return [{
            "label": CLASSES[idx],
            "confidence": confidence,
            "bbox": None
        }]


def annotate_image(image, objects):
    if objects and len(objects) > 0:
        obj = objects[0]
        print(obj['confidence'])
        label = obj['label']
        if label != "Processing":
            text = f"{label}"
            # text = f"{label}: {obj['confidence']:.2f}"
        else:
            text = label

        cv2.putText(image, text, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
    return image


class ImageStreamNode(Node):
    def __init__(self):
        super().__init__('disease_detector_node')

        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

        self.pub_original = self.create_publisher(Image, '/image_original', 10)
        self.pub_compressed = self.create_publisher(CompressedImage, '/image_compressed', 10)
        self.pub_annotated = self.create_publisher(Image, '/image_annotated', 10)
        self.pub_inference = self.create_publisher(String, '/inference_result', 10)

    def image_callback(self, msg):
        global latest_raw, latest_compressed, latest_annotated, latest_metadata
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            latest_raw = cv_image
            self.pub_original.publish(msg)

            # Compressed original
            _, jpeg = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            compressed_msg = CompressedImage()
            compressed_msg.header = msg.header
            compressed_msg.format = 'jpeg'
            compressed_msg.data = jpeg.tobytes()
            self.pub_compressed.publish(compressed_msg)
            latest_compressed = jpeg.tobytes()

            # Run detection/classification
            objects = detect_objects(cv_image)
            annotated = annotate_image(cv_image.copy(), objects)

            annotated_msg = bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
            annotated_msg.header = msg.header
            self.pub_annotated.publish(annotated_msg)

            _, annotated_jpeg = cv2.imencode('.jpg', annotated)
            latest_annotated = annotated_jpeg.tobytes()

            detected_label = objects[0]['label'] if objects else "Processing"
            latest_metadata = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "objects": objects,
                "num_objects": len(objects)
            }

            msg_label = String()
            msg_label.data = detected_label
            self.pub_inference.publish(msg_label)

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
    # Thread(target=start_http_server, daemon=True).start()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()