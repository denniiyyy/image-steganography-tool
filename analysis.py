# analysis.py - functions to calculate MSE, PSNR, SSIM, entropy and plot histograms

import os
import math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def calculate_entropy(image_array):
    # calculate Shannon entropy of pixel values
    hist, _ = np.histogram(image_array, bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


def calculate_mse(img1, img2):
    # mean squared error between two images
    diff = img1.astype(np.float64) - img2.astype(np.float64)
    return float(np.mean(diff ** 2))


def calculate_psnr(img1, img2):
    # peak signal-to-noise ratio in dB
    mse = calculate_mse(img1, img2)
    if mse == 0:
        return float("inf")
    return float(10.0 * math.log10((255.0 ** 2) / mse))


def calculate_ssim(img1, img2):
    # structural similarity index (SSIM)
    if img1.ndim == 3 and img1.shape[2] == 3:
        # convert to grayscale for SSIM
        x = 0.2989 * img1[:, :, 0] + 0.5870 * img1[:, :, 1] + 0.1140 * img1[:, :, 2]
        y = 0.2989 * img2[:, :, 0] + 0.5870 * img2[:, :, 1] + 0.1140 * img2[:, :, 2]
    else:
        x = img1.astype(np.float64)
        y = img2.astype(np.float64)

    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    mu_x = np.mean(x)
    mu_y = np.mean(y)
    sigma_x_sq = np.var(x)
    sigma_y_sq = np.var(y)
    sigma_xy = np.mean((x - mu_x) * (y - mu_y))

    num = (2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)
    den = (mu_x ** 2 + mu_y ** 2 + c1) * (sigma_x_sq + sigma_y_sq + c2)
    return float(num / den)


def analyze_images(cover_path, stego_path):
    # compare cover and stego images
    if not os.path.exists(cover_path):
        raise FileNotFoundError(f"Cover image not found: {cover_path}")
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")

    with Image.open(cover_path) as c_img, Image.open(stego_path) as s_img:
        cover_rgb = np.array(c_img.convert("RGB"), dtype=np.uint8)
        stego_rgb = np.array(s_img.convert("RGB"), dtype=np.uint8)

    if cover_rgb.shape != stego_rgb.shape:
        raise ValueError("Image dimensions do not match.")

    height, width, channels = cover_rgb.shape
    total_pixels = height * width

    # calculate quality metrics
    mse = calculate_mse(cover_rgb, stego_rgb)
    psnr = calculate_psnr(cover_rgb, stego_rgb)
    ssim = calculate_ssim(cover_rgb, stego_rgb)

    # count modified pixels
    diff_abs = np.abs(cover_rgb.astype(np.int32) - stego_rgb.astype(np.int32))
    modified_channels = int(np.sum(diff_abs > 0))
    modified_pixels = int(np.sum(np.any(diff_abs > 0, axis=2)))

    # file sizes and entropy
    cover_file_size = os.path.getsize(cover_path)
    stego_file_size = os.path.getsize(stego_path)
    size_delta = stego_file_size - cover_file_size
    size_change_pct = (size_delta / cover_file_size) * 100.0 if cover_file_size > 0 else 0.0

    cover_entropy = calculate_entropy(cover_rgb)
    stego_entropy = calculate_entropy(stego_rgb)

    if psnr > 50:
        visual_desc = "Imperceptible (PSNR > 50 dB indicates changes cannot be seen by naked eye)."
    elif psnr > 40:
        visual_desc = "Good quality (near imperceptible)."
    else:
        visual_desc = "Noticeable differences."

    return {
        "dimensions": f"{width}x{height}",
        "total_pixels": total_pixels,
        "mse": mse,
        "psnr_db": psnr,
        "ssim": ssim,
        "modified_pixels": modified_pixels,
        "modified_pixels_pct": (modified_pixels / total_pixels) * 100.0,
        "cover_file_size": cover_file_size,
        "stego_file_size": stego_file_size,
        "size_delta_bytes": size_delta,
        "size_change_pct": size_change_pct,
        "cover_entropy": cover_entropy,
        "stego_entropy": stego_entropy,
        "visual_assessment": visual_desc,
    }


def plot_histograms(cover_path, stego_path, save_path=None):
    # plot RGB histograms comparing cover vs stego
    with Image.open(cover_path) as c_img, Image.open(stego_path) as s_img:
        cover_arr = np.array(c_img.convert("RGB"), dtype=np.uint8)
        stego_arr = np.array(s_img.convert("RGB"), dtype=np.uint8)

    fig, axes = plt.subplots(3, 2, figsize=(13, 9))
    fig.suptitle("RGB Histogram Analysis: Cover vs Stego Image", fontsize=14, fontweight="bold")

    channels = [("Red", 0, "#d9534f"), ("Green", 1, "#5cb85c"), ("Blue", 2, "#0275d8")]

    for name, idx, color in channels:
        c_vals = cover_arr[:, :, idx].flatten()
        s_vals = stego_arr[:, :, idx].flatten()

        c_hist, _ = np.histogram(c_vals, bins=256, range=(0, 256))
        s_hist, _ = np.histogram(s_vals, bins=256, range=(0, 256))

        # histogram comparison
        ax_hist = axes[idx, 0]
        ax_hist.plot(c_hist, color=color, alpha=0.85, label=f"Cover {name}")
        ax_hist.plot(s_hist, color="#333333", linestyle="--", alpha=0.75, label=f"Stego {name}")
        ax_hist.set_title(f"{name} Channel - Histogram")
        ax_hist.set_xlabel("Pixel Value [0-255]")
        ax_hist.set_ylabel("Count")
        ax_hist.set_xlim(0, 255)
        ax_hist.grid(True, linestyle=":", alpha=0.5)
        ax_hist.legend()

        # histogram difference (stego - cover)
        ax_diff = axes[idx, 1]
        diff_hist = s_hist.astype(np.int64) - c_hist.astype(np.int64)
        ax_diff.bar(range(256), diff_hist, color=color, alpha=0.7, width=1.0)
        ax_diff.axhline(0, color="black", linestyle="--", linewidth=0.8)
        ax_diff.set_title(f"{name} Channel - Difference (Stego - Cover)")
        ax_diff.set_xlabel("Pixel Value [0-255]")
        ax_diff.set_ylabel("Delta")
        ax_diff.set_xlim(0, 255)
        ax_diff.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    return fig


def plot_visual_comparison(cover_path, stego_path, save_path=None):
    # visual side by side and amplified difference map
    with Image.open(cover_path) as c_img, Image.open(stego_path) as s_img:
        cover_arr = np.array(c_img.convert("RGB"), dtype=np.uint8)
        stego_arr = np.array(s_img.convert("RGB"), dtype=np.uint8)

    diff_arr = np.abs(cover_arr.astype(np.int32) - stego_arr.astype(np.int32)).astype(np.uint8)
    # amplify differences by 20x so changes are visible
    amplified_diff = np.clip(diff_arr * 20, 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Visual Comparison and Difference Map", fontsize=14, fontweight="bold")

    axes[0].imshow(cover_arr)
    axes[0].set_title("Original Cover Image")
    axes[0].axis("off")

    axes[1].imshow(stego_arr)
    axes[1].set_title("Stego Image")
    axes[1].axis("off")

    axes[2].imshow(amplified_diff)
    axes[2].set_title("Difference Map (Amplified 20x)")
    axes[2].axis("off")

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    return fig
