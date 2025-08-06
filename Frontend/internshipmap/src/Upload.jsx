import { useState } from "react";
import axios from 'axios';
import JobMatch from "./JobMatch";
import { Navigate, useNavigate } from "react-router-dom";

function ResumeUpload() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [parsedData, setParsedData] = useState(null);
    const navigate = useNavigate();


    const handFileSelection = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleFileUpload = async() => {
        if(!selectedFile) {
            setUploadStatus("Select file first") ;
            return;
        }

        setUploadStatus("Uploading");
        const formData = new FormData();
        formData.append('resume', selectedFile);

        try {
            const response = await axios.post('http://localhost:5000/api/upload_resume', formData, {
                                headers: { "Authorization": localStorage.getItem('token') }
                                });
            setParsedData(response.data);
            setUploadStatus("Upload Succesful");
        } catch (error) {
            setUploadStatus(`Upload failed: ${error.message}`);
        }
    };

    const handleFindJobs = () => {
        navigate('/find-jobs')
    };

    return (
        <>
            <div>
                <div className='card' style={{backgroundColor: 'darkgrey', borderRadius: 20, marginBottom: 20}}>
                    <input type="file" onChange={handFileSelection} />
                    {selectedFile && <p>Selected Resume: {selectedFile.name}</p>}
                    <button onClick={handleFileUpload} disabled={!selectedFile || uploadStatus === 'Uploading'}>
                        Upload Resume
                    </button>

                    {uploadStatus && <p>{uploadStatus}</p>}
                </div>

                {parsedData ? 
                <div className="card" style={{backgroundColor: 'darkgrey', borderRadius: 20, marginTop: 20}}>
                    <h2>Skills</h2>
                    <ul>
                        {parsedData.skills.map((skill, index) => (
                            <li key={index}>{skill}</li>
                        ))}
                    </ul>

                    <h2>Projects</h2>
                    {parsedData.projects.map((proj, index) => (
                        <div key={index}>
                            <h3>{proj.name}</h3>
                            <p>{proj.summary}</p>
                            <p><strong>Technologies:</strong> {proj.technologies.join(", ")}</p>
                        </div>
                    ))}

                    <h2>Experience</h2>
                    {parsedData.experience.map((exp, index) => (
                        <div key={index}>
                            <h3>{exp.title} @ {exp.company}</h3>
                            <p>{exp.summary}</p>
                            {exp.technologies.length > 0 && (
                                <p><strong>Tools:</strong> {exp.technologies.join(", ")}</p>
                            )}
                        </div>
                    ))}
                    <br/><br/>
                    <button onClick={handleFindJobs}>Find Jobs</button>
                </div>
                : 
                    <p>No Resume Uploaded Yet</p>}
            </div>
        </>
    )
}

export default ResumeUpload