import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let args = CommandLine.arguments
let pdf = CGPDFDocument(URL(fileURLWithPath: args[1]) as CFURL)!
let outDir = args[2]; let width = CGFloat(Double(args[3])!)
for i in 1...pdf.numberOfPages {
  let page = pdf.page(at: i)!
  let box = page.getBoxRect(.mediaBox)
  let s = width / box.width; let h = Int(box.height * s)
  let ctx = CGContext(data: nil, width: Int(width), height: h, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
  ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: Int(width), height: h))
  ctx.scaleBy(x: s, y: s); ctx.drawPDFPage(page)
  let url = URL(fileURLWithPath: String(format: "%@/p%02d.png", outDir, i)) as CFURL
  let dest = CGImageDestinationCreateWithURL(url, UTType.png.identifier as CFString, 1, nil)!
  CGImageDestinationAddImage(dest, ctx.makeImage()!, nil); CGImageDestinationFinalize(dest)
}
