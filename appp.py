import streamlit as st
import pandas as pd
import os
import requests
from zipfile import ZipFile
import tempfile

st.title("📄 COI Downloader!")

subid_input = st.text_area("Enter SubIDs (one per line):")
subids = subid_input.strip().splitlines() if subid_input else []

name_input = st.text_area("Enter Names (one per line):")
names = name_input.strip().splitlines() if name_input else []

zipfileName = st.text_input("Enter the Zip file")

fileNames = []

for i in names:
    fileNames.append(i+" Health Insurance COI")
    fileNames.append(i+" Personal Accident COI")

links = []

for j in subids:
    links.append("https://api.clinikk.com/v4/subscriptions/" + j + "/coi/download?insuranceType=health")
    links.append("https://api.clinikk.com/v4/subscriptions/" + j + "/coi/download?insuranceType=accidental")


toDownload = pd.DataFrame({"Name of PDF" : fileNames, "Downloadable_links" : links})

if st.button("Download and Zip PDFs"):
    with st.spinner("Downloading PDFs and zipping..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_folder = os.path.join(tmpdir, "pdfs")
            os.makedirs(pdf_folder, exist_ok=True)

            toDownload["Downloaded Status"] = ""

            for idx, row in toDownload.iterrows():
                url = row[toDownload.columns[1]]
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    filename = f"file_{row[toDownload.columns[0]]}.pdf"
                    filepath = os.path.join(pdf_folder, filename)

                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    toDownload.at[idx, "Downloaded Status"] = "Downloaded"
                except Exception as e:
                    toDownload.at[idx, "Downloaded Status"] = f"Failed: {e}"

            zip_path = os.path.join(tmpdir, "Coi.zip")
            with ZipFile(zip_path, 'w') as zipf:
                for file_name in os.listdir(pdf_folder):
                    zipf.write(os.path.join(pdf_folder, file_name), arcname=file_name)

            st.success("All PDFs downloaded and zipped!")

            with open(zip_path, 'rb') as f:
                st.download_button("📥 Download ZIP", f, file_name=f"{zipfileName}.zip")

    st.write("Download Status:")
    missingData = toDownload[toDownload["Downloaded Status"] != "Downloaded"]
    st.dataframe(missingData)

    st.write("✅ Download complete! Enjoy a reminder tune below:")
    st.video("https://www.youtube.com/watch?v=ED2EgbsDXDc",loop=True, autoplay=True)  # Replace with any YouTube music URL
