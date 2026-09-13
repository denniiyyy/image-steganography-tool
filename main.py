# main.py - entry point for running steganography tool (GUI or CLI)

import sys
import os
import argparse


def main():
    # if no arguments given, open the GUI
    if len(sys.argv) == 1:
        from gui import launch_gui
        launch_gui()
        return

    parser = argparse.ArgumentParser(description="Steganography Tool (IKB 21303)")
    subparsers = parser.add_subparsers(dest="command")

    # embed command
    p_embed = subparsers.add_parser("embed", help="Hide secret file inside cover image")
    p_embed.add_argument("--cover", "-c", required=True, help="Cover image path")
    p_embed.add_argument("--secret", "-s", required=True, help="Secret file path")
    p_embed.add_argument("--output", "-o", default="output/stego.png", help="Output stego image path")

    # extract command
    p_extract = subparsers.add_parser("extract", help="Extract hidden file from stego image")
    p_extract.add_argument("--stego", "-i", required=True, help="Stego image path")
    p_extract.add_argument("--dest", "-d", default="output/extracted", help="Destination folder or file path")

    # analyze command
    p_analyze = subparsers.add_parser("analyze", help="Compare cover and stego images")
    p_analyze.add_argument("--cover", "-c", required=True, help="Cover image path")
    p_analyze.add_argument("--stego", "-s", required=True, help="Stego image path")
    p_analyze.add_argument("--chart", help="Optional path to save histogram plot")

    # test-all command
    subparsers.add_parser("test-all", help="Run test suite on all sample files")

    args = parser.parse_args()

    if args.command == "embed":
        from stego_core import hide_data
        print(f"Embedding {args.secret} into {args.cover}...")
        res = hide_data(args.cover, args.secret, args.output)
        print(f"Done! Saved to: {res['output_path']}")
        print(f"Payload: {res['payload_bytes']:,} bytes | Bits modified: {res['bits_modified']:,}")

    elif args.command == "extract":
        from stego_core import extract_data
        print(f"Extracting secret file from {args.stego}...")
        res = extract_data(args.stego, args.dest)
        print("Done!")
        print(f"Format: {res['file_extension']} | Size: {res['payload_size']:,} bytes | CRC32: {res['crc32']}")
        print(f"Saved to: {res['saved_path']}")

    elif args.command == "analyze":
        from analysis import analyze_images, plot_histograms
        print(f"Analyzing {args.cover} vs {args.stego}...")
        m = analyze_images(args.cover, args.stego)
        print("-" * 45)
        print(f"Resolution:      {m['dimensions']}")
        print(f"MSE:             {m['mse']:.6f}")
        print(f"PSNR:            {m['psnr_db']:.2f} dB")
        print(f"SSIM:            {m['ssim']:.4f}")
        print(f"Modified Pixels: {m['modified_pixels']:,} ({m['modified_pixels_pct']:.2f}%)")
        print(f"Cover Size:      {m['cover_file_size']:,} bytes")
        print(f"Stego Size:      {m['stego_file_size']:,} bytes")
        print(f"Size Delta:      {m['size_delta_bytes']:+,} bytes ({m['size_change_pct']:+.2f}%)")
        print(f"Cover Entropy:   {m['cover_entropy']:.4f}")
        print(f"Stego Entropy:   {m['stego_entropy']:.4f}")
        print("-" * 45)

        if args.chart:
            plot_histograms(args.cover, args.stego, save_path=args.chart)
            print(f"Histogram chart saved to: {args.chart}")

    elif args.command == "test-all":
        from run_analysis import run_full_suite
        run_full_suite()


if __name__ == "__main__":
    main()
