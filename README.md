# TFTP Client

This README file provides instructions for compiling and running the `tftp_client.py` Python program. It also includes a description of the implemented features and error-handling mechanisms.

## Instructions for Compiling and Running

### Prerequisites
- Python 3.x installed on your system

### Running the Program

1. Open a terminal or command prompt.
2. Navigate to the directory containing `tftp_client.py`.
3. Run the program using the following command:
    ```sh
    python tftp_client.py
    ```

## Features

- **File Download**: Allows users to download files from a TFTP server.
- **File Upload**: Enables users to upload files to a TFTP server.
- **Server Address Configuration**: Users can specify the TFTP server address and port.
- **Graphical User Interface (GUI)**: Provides a user-friendly GUI for easier interaction.

## Error-Handling Mechanisms

- **Connection Errors**: Handles errors related to network connectivity and server availability.
- **File Not Found**: Provides user-friendly messages when the requested file is not found on the server.
- **Timeouts**: Implements retry logic for operations that time out.
- **Invalid Inputs**: Validates user inputs and provides appropriate error messages for invalid entries.

## Test Cases
IP Address of the server is **127.0.0.1**

| Test Case | Description                          | Expected Result                       | Input           | Pass/Fail |
|-----------|--------------------------------------|---------------------------------------|-----------------|:---------:|
|    1      | Download a text file from the server | File is downloaded successfully       | download.txt    |   Pass    |
|    2      | Download a jpg file from the server  | File is downloaded successfully       | download.jpg    |   Pass    |
|    3      | Download a bin file from the server  | File is downloaded successfully       | download.bin    |   Pass    |
|    4      | Upload a text file to the server     | File is uploaded successfully         | upload.txt      |   Pass    |
|    5      | Upload a jpg file to the server      | File is uploaded successfully         | upload.jpg      |   Pass    |
|    6      | Upload a bin file to the server      | File is uploaded successfully         | upload.bin      |   Pass    |
|    7      | Input an invalid IP address          | Error message is displayed            | 127.0.0.0       |   Pass    |
|    8      | File extensions don't match when downloading/uploading a file | Error message is displayed | download.txt & download.bin |   Pass    |
