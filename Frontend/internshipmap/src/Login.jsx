import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import ResumeUpload from "./Upload";

function Login({ onLogin }){
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [status, setStatus] = useState('');
    const navigate = useNavigate();

    const handleLogin = async() => {
        try {
            const response = await axios.post('http://localhost:5001/login', {email, password});
            setStatus("Login Successful");
            onLogin(response.data);
            localStorage.setItem('token', response.data.token);
            navigate('/dashboard')
        } catch (error){
            setStatus("Login failed: " + err.response?.data?.error || err.message);
        }
    };

    return (
        <div className="card" style={{borderRadius: 20}}>
            <h2>Login</h2>
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}/>
            <br /> <br />
            <h2>Password</h2>
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <br/><br/>
            <button onClick={handleLogin}>Login</button>
            {status && <p>{status}</p>}
        </div>
    );
}

export default Login