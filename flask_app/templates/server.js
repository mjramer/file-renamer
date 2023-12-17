require('dotenv').config();
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const path = require('path'); // Add this line
const cors = require('cors'); // Add this line
const accessKey = process.env.API_KEY
const secretAccessKey = process.env.API_KEY
const region = process.env.REGION

const app = express();
const port = 3000;

// Enable CORS
app.use(cors());

// Configure AWS SDK
AWS.config.update({
    accessKeyId: accessKey,
    secretAccessKey: secretAccessKey,
    region: region,
});

const s3 = new AWS.S3();

// Configure Multer for file uploads
const upload = multer({ dest: 'uploads/' });

app.post('/upload', upload.array('files'), (req, res) => {
    const files = req.files;

    if (!files || files.length === 0) {
        return res.status(400).send('No files uploaded.');
    }

    const promises = files.map(file => {
        const s3Key = path.join('multi-pdfs', file.originalname); // Update the S3 key
        const params = {
            Bucket: 'feefs-pdfs',
            Key: s3Key,
            Body: require('fs').createReadStream(file.path),
        };

        s3.upload(params, (err, data) => {
            if (err) {
              console.error('Error uploading to S3:', err);
            } else {
              console.log('File uploaded to S3:', data.Location);
        
              // Execute Python script after successful upload
              executePythonScript();
            }
        });
    });

    // Promise.all(promises)
    //     .then(data => {
    //         console.log('Upload success:', data);
    //         res.status(200).send('Files uploaded successfully.');
    //     })
    //     .catch(error => {
    //         console.error('Upload error:', error);
    //         res.status(500).send('Internal Server Error');
    //     });
});

function executePythonScript() {
    console.log("Executing python script")
    const { exec } = require('child_process');
    exec('source /Users/maxramer/Desktop/file-renamer/venv/bin/activate && python /Users/maxramer/Desktop/file-renamer/src/main.py', (error, stdout, stderr) => {
    if (error) {
        console.error(`Error executing Python script: ${error}`);
        return;
    }

    console.log(`Python script executed successfully: ${stdout}`);
    });
}

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
