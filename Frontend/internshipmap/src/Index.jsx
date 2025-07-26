import React from "react";
import { Routes, Route, BrowserRouter } from "react-router-dom"

import Login from "./Login";
import Register from "./Register";
import ResumeUpload from "./Upload";

function Index(){
    return(
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<Register />}></Route>
                <Route path='/login' element={<Login/>} />
                <Route path='/dashboard' element={<ResumeUpload/>} />
            </Routes>
        </BrowserRouter>
    );
}

export default Index