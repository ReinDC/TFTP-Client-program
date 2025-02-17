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
- **Timeout and Retries**: Configurable timeout and retry attempts for reliable file transfers.
- **Graphical User Interface (GUI)**: Provides a user-friendly GUI for easier interaction.

## Error-Handling Mechanisms

- **Connection Errors**: Handles errors related to network connectivity and server availability.
- **File Not Found**: Provides user-friendly messages when the requested file is not found on the server.
- **Permission Denied**: Alerts users when they do not have permission to access the requested file.
- **Timeouts**: Implements retry logic for operations that time out.
- **Invalid Inputs**: Validates user inputs and provides appropriate error messages for invalid entries.

For more detailed information, please refer to the comments and documentation within the `tftp_client.py` source code.
