import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useState } from "react";

function JobMatch() {
    const navigate = useNavigate();
    const [jobData, setJobData] = useState(null);
    const [status, setStatus] = useState("");

    const handleJobData = async () => {
        setStatus("Finding Jobs...");

        try {
            let response = await axios.get('http://localhost:5002/api/get_jobs', {
                headers: { "Authorization": localStorage.getItem('token') }
            });

            if (response.data.message === "no jobs generated") {
                response = await axios.get('http://localhost:5002/api/match_jobs', {
                    headers: { "Authorization": localStorage.getItem('token') }
                });
            }

            setJobData(response.data);
            setStatus("Jobs Found");
        } catch (error) {
            setStatus(`Fetch failed: ${error.message}`);
        }
    };

    const handleJobClick = (job) => {
        navigate('/job-details', { state: { job } });
    };

    const handleReturn = () => {
        navigate('/dashboard');
    };

    return (
        <div style={{ padding: '2rem' }}>
            <button onClick={handleJobData} style={styles.button}>Find Jobs</button>
            <p>{status}</p>

            {jobData ? (
                <div style={styles.grid}>
                    {jobData.map((job, index) => (
                        <div key={index} style={styles.card} onClick={() => handleJobClick(job)}>
                            <h3>{job.title} | <span style={{ color: "#247a39ff" }}>{job.fit}% Fit</span></h3>
                            <p style={styles.subtext}>{job.organization}</p>
                            <p style={styles.subtext}>{job.date_posted}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <p>Click above to find matched jobs.</p>
            )}

            <br />
            <button onClick={handleReturn} style={styles.secondaryButton}>Return to Resume Upload</button>
        </div>
    );
}

const styles = {
    grid: {
        display: 'grid',
        gap: '1.5rem',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        marginTop: '2rem'
    },
    card: {
        padding: '1rem',
        borderRadius: '12px',
        backgroundColor: '#828080ff',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        cursor: 'pointer',
        transition: '0.3s',
    },
    subtext: {
        color: 'lightgray',
        margin: 0
    },
    button: {
        padding: '0.75rem 1.5rem',
        fontSize: '16px',
        borderRadius: '8px',
        backgroundColor: '#007bff',
        color: '#fff',
        border: 'none',
        cursor: 'pointer'
    },
    secondaryButton: {
        padding: '0.5rem 1rem',
        fontSize: '14px',
        marginTop: '2rem',
        backgroundColor: '#6c757d',
        color: '#fff',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer'
    }
};

export default JobMatch;