const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const path = require('path'); // Add this line
const cors = require('cors'); // Add this line

const app = express();
const port = 3000;

// Enable CORS
app.use(cors());

// Configure AWS SDK
AWS.config.update({
    accessKeyId: 'AKIAQHUQ7EWAAQABZTAL',
    secretAccessKey: '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',
    region: 'us-east-1',
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

        return s3.upload(params).promise();
    });

    Promise.all(promises)
        .then(data => {
            console.log('Upload success:', data);
            res.status(200).send('Files uploaded successfully.');
        })
        .catch(error => {
            console.error('Upload error:', error);
            res.status(500).send('Internal Server Error');
        });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
