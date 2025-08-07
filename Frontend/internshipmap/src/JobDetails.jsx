import { useNavigate, useLocation } from "react-router-dom";

function JobDetails() {
    const location = useLocation();
    const navigate = useNavigate();

    const job = location.state?.job;

    if (!job) {
        return <h3 style={{ textAlign: "center", marginTop: "2rem" }}>No Job Details Available</h3>;
    }

    const handleReturn = () => {
        navigate('/find-jobs');
    };

    return (
        <div style={{ padding: '2rem' }}>
            <div style={styles.card}>
                <h2>{job.title} | {job.fit}% Fit</h2>
                <p style={styles.subtext}>{job.organization} | {job.location}</p>
                <p style={styles.subtext}>{job.date_posted}</p>
                <p><strong>Source:</strong> <a href={job.url} target="_blank" rel="noopener noreferrer">{job.url}</a></p>
                <hr />
                <h4>Description</h4>
                <p>{job.description}</p>
                {job.why && <>
                    <h4>Why this job?</h4>
                    <p>{job.why}</p>
                </>}
                {job.improvement && <>
                    <h4>Suggested Resume Improvements</h4>
                    <p>{job.improvement}</p>
                </>}
            </div>
            <button onClick={handleReturn} style={styles.button}>Back to Job Matches</button>
        </div>
    );
}

const styles = {
    card: {
        backgroundColor: '#757575',
        padding: '1.5rem',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        marginBottom: '2rem'
    },
    subtext: {
        color: 'lightgray',
        margin: '0.25rem 0'
    },
    button: {
        padding: '0.75rem 1.5rem',
        fontSize: '16px',
        borderRadius: '8px',
        backgroundColor: '#007bff',
        color: '#fff',
        border: 'none',
        cursor: 'pointer'
    }
};

export default JobDetails;
