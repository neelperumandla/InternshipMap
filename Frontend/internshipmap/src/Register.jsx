import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import ResumeUpload from "./Upload";

function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [status, setStatus] = useState('');
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            // Register user
            const response = await axios.post("http://localhost:5001/signup", {
                email,
                password
            });

            // Auto-login after successful registration
            const loginRes = await axios.post("http://localhost:5001/login", {
                email,
                password
            });

            // Store user info or token if your backend returns it
            localStorage.setItem("user", JSON.stringify(loginRes.data));
            localStorage.setItem('token', loginRes.data.token);

            setStatus(response.data);
            navigate('/dashboard'); // or "/home", depending on your route
        } catch (err) {
            setStatus("Error: " + (err.response?.data?.error || err.message));
        }
    };

    return (
        <>
        <div className="card" style={{borderRadius: 20}}>
            <h2>Register</h2>
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            /><br />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            /><br />
            <button onClick={handleRegister}>Sign Up</button>
            {status && <p>{status}</p>}
            <br/><br/>
            
        </div>
        </>
    );
}

export default Register;