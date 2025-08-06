import React from "react";
import { Routes, Route, BrowserRouter } from "react-router-dom"

import Login from "./Login";
import Register from "./Register";
import ResumeUpload from "./Upload";
import JobMatch from "./JobMatch";
import JobDetails from "./JobDetails";

function Index(){
    return(
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<Register />}></Route>
                <Route path='/login' element={<Login/>} />
                <Route path='/dashboard' element={<ResumeUpload/>} />
                <Route path='/find-jobs' element={<JobMatch />} />
                <Route path='/job-details' element={<JobDetails/>} />
                {/* <Route path='/upload' element={<ResumeUpload/>} /> */}
            </Routes>
        </BrowserRouter>
    );
}

export default Index