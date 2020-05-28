# File Storage App API REST

This documentation contains all the endpoints in the file storage application and how to use them.

## File

This controller is used for the upload and download methods.

### `/files/upload`
----
This endpoint uploads a file to the upload folder.

* **Method:** `POST`

* **Headers:** `None`
  
* **URL Params:** `None`

* **Body:** `{"file": <Attached file>}`

* **Success Response:**

  * **Code:** `200 OK` <br />
    **Content:**   
      ```
        {
          "fileName": "1590702505221_copia_de_book_rh.py",
          "fileDownloadUri": "http://localhost:8080/files/download/1590702505221_copia_de_book_rh.py",
          "fileType": "application/octet-stream",
          "size": 827
        }
      ```
 
* **Error Response:**

  * **Code:** `400 BAD REQUEST` <br />
    **Content:**
      ```
        {
          "timestamp": "2020-05-14T15:25:59.186+0000",
          "status": 400,
          "error": "Bad Request",
          "message": "File size exceeds 20 MB!",
          "path": "/files/upload"
        }
      ```

### `/files/download/{fileName:.+}`
----
This endpoint the file if it exists.

* **Method:** `GET`

* **Headers:** `None`
  
* **URL Params:** `None`

* **Body:** `None`

* **Success Response:**

  * **Code:** `200 OK` <br />
    **Content:** `1590702505221_copia_de_book_rh.py`
 
* **Error Response:**

  * **Code:** `404 NOT FOUND` <br />
    **Content:**
      ```
        {
          "timestamp": "2020-05-28T21:50:35.863+0000",
          "status": 404,
          "error": "Not Found",
          "message": "File not found hola.py",
          "path": "/files/download/hola.py"
        }
      ```