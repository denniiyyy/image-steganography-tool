# Image Steganography Suite (IKB 21303)

A robust, spatial-domain **Least Significant Bit (LSB) Image Steganography Tool** developed for **Universiti Kuala Lumpur - Malaysian Institute of Information Technology (UniKL MIIT)** under course **IKB 21303: Cryptography and Steganography (Assignment 2)**.

This suite provides both a user-friendly **Graphical User Interface (GUI)** and a scriptable **Command-Line Interface (CLI)** to hide, extract, verify, and statistically analyze arbitrary secret files embedded inside lossless 24-bit PNG carrier images.

---

## 👥 Project Team

| No. | Student Name | Student ID |
|:---:|:---|:---:|
| 1 | **AHMAD DANIAL HAZIQ BIN IBRAHIM** | 52215125773 |
| 2 | **ADAM HAZIQ BIN DANIANTO** | 52212125275 |
| 3 | **ALIA MARDHIAH BINTI OSMERA** | 52215251640 |
| 4 | **AHMAD AZFAR BIN MOHMMAD** | 52215125999 |

---

## 🌟 Key Features

- **Spatial-Domain LSB Substitution**: Modifies only the least significant bit (LSB) of RGB channels (1 bit per color channel, up to 3 bits per pixel) to preserve high visual fidelity.
- **Universal Payload Support**: Embed any file format seamlessly, including plain text (`.txt`), formatted documents (`.docx`, `.pdf`), images (`.png`, `.jpg`), and binary archives.
- **Custom Packet Structure**: Embeds magic header metadata, dynamic extension strings, payload length, and raw bytes.
- **Built-in Integrity Verification**: Computes and validates a 32-bit CRC-32 checksum during extraction to guarantee that secret data has not been corrupted or tampered with.
- **Lossless PNG Pipeline**: Enforces PNG encoding to prevent lossy compression algorithms (such as JPEG discrete cosine transform quantization) from destroying concealed data bits.
- **Steganalysis & Metric Evaluation**:
  - **MSE (Mean Squared Error)**: Measures average squared pixel intensity discrepancies.
  - **PSNR (Peak Signal-to-Noise Ratio)**: Quantifies imperceptibility (typically $> 50\text{ dB}$).
  - **SSIM (Structural Similarity Index Measure)**: Evaluates structural, luminance, and contrast consistency.
  - **Shannon Entropy**: Evaluates carrier randomness before and after embedding.
  - **Pixel Delta Analysis**: Calculates exact modified pixel count and percentage.
- **RGB Histogram Visualization**: Side-by-side comparative histogram curves and delta bar charts (`Stego - Cover`) for each color channel.
- **Dual Interface**: Modern multi-tab Tkinter desktop GUI and flexible command-line flags.

---

## 📁 Repository Structure

```text
.
├── HOW TO RUN.txt       # Quick plain-text launch notes
├── README.md            # Comprehensive project documentation
├── requirements.txt     # Python package dependencies
├── run.bat              # One-click Windows batch launcher
├── main.py              # CLI / GUI application entry point
├── gui.py               # Tkinter GUI (Tabbed interface & Matplotlib canvas)
├── stego_core.py        # Core LSB embedding, extraction, & packet formatting
├── analysis.py          # Quality metrics (MSE, PSNR, SSIM, Entropy) & plotting
├── screenshots/         # Application UI screenshots
│   ├── tab1_embed.png   # Tab 1: Embed screen
│   ├── tab2_extract.png # Tab 2: Extract screen
│   ├── tab3_analysis.png# Tab 3: Analysis & Histogram screen
│   └── tab4_about.png   # Tab 4: About & Instructions screen
├── samples/             # Sample cover and secret payload files
│   ├── cover.png        # Sample carrier image (742x983)
│   ├── secret.docx      # Sample Word document
│   ├── secret.jpg       # Sample JPEG image
│   ├── secret.pdf       # Sample PDF document
│   ├── secret.png       # Sample PNG image
│   └── secret.txt       # Sample plain text file
└── output/              # Default destination folder for stego & extracted files
    ├── stego.png        # Generated stego image
    └── extracted/       # Destination folder for extracted files
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8** or newer installed. Ensure Python is added to your system `PATH`.

### 2. Installation
Clone or extract the repository, open a terminal / command prompt inside the project folder, and install the required dependencies:

```bash
pip install -r requirements.txt
```

*Dependencies installed:*
- `Pillow` (PIL) - Image loading, color conversion, and lossless PNG saving.
- `numpy` - Fast array bitwise operations and channel manipulation.
- `matplotlib` - Comparative RGB histogram generation and visual difference maps.

---

## 🖥️ Usage

### Option A: Graphical User Interface (GUI)

You can launch the GUI using either of the following methods:

1. **One-Click Batch Runner (Windows)**:
   Double-click `run.bat` in File Explorer.

2. **Terminal / Command Prompt**:
   ```bash
   python main.py
   ```

#### GUI Tabs Overview:
- **Hide Data (Embed)**:
  - Browse cover image and secret file.
  - Live carrier capacity calculation (width, height, total carrier bits, max payload size).
  - One-click file hiding with direct output folder opening.
- **Extract Data (Reveal)**:
  - Select any stego PNG image.
  - Automatically reads packet metadata, restores original file extension, checks CRC-32 integrity, and saves the extracted file.
- **Quality & Histogram Analysis**:
  - Compare Cover vs. Stego image.
  - Displays MSE, PSNR (dB), SSIM, and byte delta KPIs.
  - Renders embedded interactive Red, Green, and Blue channel histogram curves alongside delta distribution charts.
- **About & Instructions**:
  - Course information, student credentials, and operating guidelines.

---

## 🖼️ User Interface (UI) Screenshots

### 1. Hide Data (Embed) Tab
The **Hide Data** tab allows users to select a carrier image and secret payload file. It computes carrier capacity in real-time, displays image dimensions, and embeds the payload using 1-bit LSB substitution.

![Tab 1 - Hide Data (Embed)](screenshots/tab1_embed.png)

---

### 2. Extract Data (Reveal) Tab
The **Extract Data** tab enables users to load any stego image to reveal hidden content. It reads packet headers, detects the original file format, validates data integrity using CRC-32, and saves the recovered file.

![Tab 2 - Extract Data (Reveal)](screenshots/tab2_extract.png)

---

### 3. Quality & Histogram Analysis Tab
The **Quality & Histogram Analysis** tab calculates quantitative image fidelity metrics (MSE, PSNR, SSIM, Entropy, and File Size Delta) and displays comparative Red, Green, and Blue channel histogram curves and difference distribution charts.

![Tab 3 - Quality & Histogram Analysis](screenshots/tab3_analysis.png)

---

### 4. About & Instructions Tab
The **About & Instructions** tab provides course information, group member details, supported formats, and operating instructions.

![Tab 4 - About & Instructions](screenshots/tab4_about.png)

---


## 📊 Metrics & Quality Benchmark Reference

| Metric | Formula / Basis | Ideal Value | Description |
|:---|:---|:---:|:---|
| **MSE** | $\frac{1}{MN} \sum (I - K)^2$ | $\approx 0$ | Lower is better; 0 means mathematically identical. |
| **PSNR** | $10 \log_{10}\left(\frac{255^2}{\text{MSE}}\right)$ | $> 50\text{ dB}$ | Values $> 50\text{ dB}$ are visually imperceptible to the human eye. |
| **SSIM** | $\frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$ | $\approx 1.000$ | Range $[-1, 1]$. Values $\ge 0.99$ represent near-perfect structural retention. |
| **Entropy** | $-\sum p_i \log_2(p_i)$ | Baseline $\approx$ Stego | Measures information density and channel randomness. |
| **CRC-32** | ISO 3309 polynomial | Match | Cyclic Redundancy Check validating bitstream integrity. |

---


## 📜 Academic Note

This project is submitted in partial fulfillment of the coursework requirements for **IKB 21303 (Cryptography and Steganography)** at **Universiti Kuala Lumpur (UniKL MIIT)**.
