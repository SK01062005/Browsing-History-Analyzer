import cv2
import numpy as np
import pywt
import tkinter as tk
from tkinter import filedialog
import scipy.linalg

# Function to select an image file
def select_file(title="Select Image"):
    file_path = filedialog.askopenfilename(title=title, filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    return file_path

# Function to apply DWT and SVD for watermark embedding
def embed_watermark(alpha=0.1):
    # Select original image and watermark
    image_path = select_file("Select Original Image")
    watermark_path = select_file("Select Watermark Image")

    if not image_path or not watermark_path:
        print("Image selection cancelled.")
        return

    # Load images
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)

    # Resize watermark
    watermark = cv2.resize(watermark, (image.shape[1] // 2, image.shape[0] // 2))

    # Apply DWT
    coeffs = pywt.dwt2(image, 'haar')
    LL, (LH, HL, HH) = coeffs

    # Apply SVD on LL
    U, S, V = np.linalg.svd(LL, full_matrices=False)
    Uw, Sw, Vw = np.linalg.svd(watermark, full_matrices=False)

    # Modify singular values
    S_marked = S + alpha * Sw

    # Reconstruct modified LL
    LL_marked = np.dot(U, np.dot(np.diag(S_marked), V))

    # Perform inverse DWT
    watermarked_image = pywt.idwt2((LL_marked, (LH, HL, HH)), 'haar')
    watermarked_image = np.clip(watermarked_image, 0, 255).astype(np.uint8)

    # Save and show the watermarked image
    output_path = "watermarked_image.png"
    cv2.imwrite(output_path, watermarked_image)
    print(f"Watermark embedded and saved as {output_path}")
    cv2.imshow("Watermarked Image", watermarked_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Function to extract the watermark
def extract_watermark(alpha=0.1):
    # Select original and watermarked images
    original_image_path = select_file("Select Original Image")
    watermarked_image_path = select_file("Select Watermarked Image")

    if not original_image_path or not watermarked_image_path:
        print("Image selection cancelled.")
        return

    # Load images
    original_image = cv2.imread(original_image_path, cv2.IMREAD_GRAYSCALE)
    watermarked_image = cv2.imread(watermarked_image_path, cv2.IMREAD_GRAYSCALE)

    # Apply DWT
    coeffs_orig = pywt.dwt2(original_image, 'haar')
    LL_orig, _ = coeffs_orig

    coeffs_watermarked = pywt.dwt2(watermarked_image, 'haar')
    LL_watermarked, _ = coeffs_watermarked

    # Apply SVD
    Uo, So, Vo = np.linalg.svd(LL_orig, full_matrices=False)
    Uw, Sw, Vw = np.linalg.svd(LL_watermarked, full_matrices=False)

    # Extract watermark
    extracted_watermark = (Sw - So) / alpha
    extracted_watermark = np.clip(extracted_watermark, 0, 255).astype(np.uint8)

    # Save and show the extracted watermark
    output_path = "extracted_watermark.png"
    cv2.imwrite(output_path, extracted_watermark)
    print(f"Extracted watermark saved as {output_path}")
    cv2.imshow("Extracted Watermark", extracted_watermark)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# GUI for user interaction
def main():
    root = tk.Tk()
    root.title("Invisible Watermarking Tool")
    root.geometry("400x200")

    tk.Label(root, text="Invisible Watermarking for Digital Forensics", font=("Arial", 12, "bold")).pack(pady=10)

    embed_btn = tk.Button(root, text="Embed Watermark", command=embed_watermark, font=("Arial", 12))
    embed_btn.pack(pady=5)

    extract_btn = tk.Button(root, text="Extract Watermark", command=extract_watermark, font=("Arial", 12))
    extract_btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
