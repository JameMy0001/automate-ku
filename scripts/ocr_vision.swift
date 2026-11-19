import Vision
import Foundation

guard CommandLine.arguments.count > 1 else {
    print("Usage: ocr_vision <image_path>")
    exit(1)
}

let imagePath = CommandLine.arguments[1]
let url = URL(fileURLWithPath: imagePath)
let request = VNRecognizeTextRequest()
request.recognitionLanguages = ["th-TH", "en-US"]
request.recognitionLevel = .accurate

let handler = VNImageRequestHandler(url: url, options: [:])
try? handler.perform([request])

struct Item: Codable {
    let text: String
    let x: Double
    let y: Double
    let w: Double
    let h: Double
}

var items = [Item]()
if let results = request.results {
    for obs in results {
        let text = obs.topCandidates(1).first?.string ?? ""
        let box = obs.boundingBox
        items.append(Item(text: text, x: Double(box.origin.x), y: Double(box.origin.y), w: Double(box.size.width), h: Double(box.size.height)))
    }
}

let encoder = JSONEncoder()
if let data = try? encoder.encode(items), let jsonString = String(data: data, encoding: .utf8) {
    print(jsonString)
}
