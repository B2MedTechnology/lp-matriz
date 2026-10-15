// quadros-video.swift — extrai 9 quadros (0 s a ~8 s) para a folha de contato.
// É o PORTEIRO do vídeo: olhar TODOS os quadros, não só o primeiro — terceiros no
// quadro, onde a pessoa está, e se o último quadro emenda com o primeiro no laço.
//   swift quadros-video.swift <arquivo.mp4> <pasta-de-saida>
// Mais rápido compilado: swiftc -O quadros-video.swift -o quadros-video (o conferir-video.mjs usa o binário se existir)
import AVFoundation
import AppKit
let url = URL(fileURLWithPath: CommandLine.arguments[1]); let out = CommandLine.arguments[2]
let asset = AVURLAsset(url: url)
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
print("duracao", CMTimeGetSeconds(asset.duration))
for tr in asset.tracks { print("trilha", tr.mediaType.rawValue, tr.naturalSize, "fps", tr.nominalFrameRate, "kbps", tr.estimatedDataRate/1000) }
for t in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.95] {
  do {
    let cg = try gen.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil)
    let d = NSBitmapImageRep(cgImage: cg).representation(using: .jpeg, properties: [.compressionFactor: 0.9])!
    try d.write(to: URL(fileURLWithPath: String(format: "%@/f%05.2f.jpg", out, t)))
  } catch { print("erro", t, error) }
}
