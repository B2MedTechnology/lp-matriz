// ════════════════════════════════════════════════════════════════════════════
// sequencia-video.swift (v2) — decodifica o vídeo INTEIRO em ordem e grava 1 a cada
// `passo` quadros em PNG (sem perda), com os valores CRUS do decodificador.
// Serve à rolagem que arrasta o vídeo: um canvas desenha o quadro da posição.
//   swift sequencia-video.swift <video.mp4> <pasta> <passo>      (macOS; alternativa ffmpeg no README)
//
// ⚠️ SEM CONVERSÃO DE COR, de propósito (v1 usava CIImage e errava): o navegador
// mostra o <video> Rec.709 com os valores crus, lidos como sRGB. A v1 passava por
// CIImage → sRGB, que aplica a gama de vídeo da Apple e CLAREIA os meios-tons —
// medido num caso real, quadro 144: <video> no Chrome = brilho 111,8;
// quadro da v1 = 120,7. O rosto saía pálido e lavado ao lado do vídeo.
// Aqui o buffer BGRA do decodificador vira CGImage marcada sRGB SEM converter.
// Por que não arrastar o próprio <video>: o arquivo de IA tem 192 quadros e UM
// quadro-chave — cada busca decodifica desde o início, e a rolagem trava.
// Nomeia pelo tempo de APRESENTAÇÃO (há quadros B: a ordem de saída não é a de tela).
// ════════════════════════════════════════════════════════════════════════════
import AVFoundation
import AppKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let pasta = CommandLine.arguments[2]
let passo = Int(CommandLine.arguments[3]) ?? 2
let asset = AVURLAsset(url: url)
let trilha = asset.tracks(withMediaType: .video).first!
let fps = Double(trilha.nominalFrameRate)
let leitor = try! AVAssetReader(asset: asset)
let saida = AVAssetReaderTrackOutput(track: trilha, outputSettings:
  [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
leitor.add(saida); leitor.startReading()
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
var lidos = 0, gravados = 0
while let sb = saida.copyNextSampleBuffer() {
  guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
  let idx = Int((CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sb)) * fps).rounded())
  lidos += 1
  if idx % passo != 0 { continue }
  CVPixelBufferLockBaseAddress(pb, .readOnly)
  let cx = CGContext(data: CVPixelBufferGetBaseAddress(pb), width: CVPixelBufferGetWidth(pb),
                     height: CVPixelBufferGetHeight(pb), bitsPerComponent: 8,
                     bytesPerRow: CVPixelBufferGetBytesPerRow(pb), space: srgb,
                     bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)!
  let cg = cx.makeImage()!
  CVPixelBufferUnlockBaseAddress(pb, .readOnly)
  let d = NSBitmapImageRep(cgImage: cg).representation(using: .png, properties: [:])!
  try! d.write(to: URL(fileURLWithPath: String(format: "%@/q%03d.png", pasta, idx / passo)))
  gravados += 1
}
print("decodificados", lidos, "· gravados", gravados, "· fps", fps)
