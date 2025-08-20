import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Environments from './pages/Environments';
import Models from './pages/Models';
import Nodes from './pages/Nodes';
import Deployments from './pages/Deployments';
import Scheduling from './pages/Scheduling';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/environments" element={<Environments />} />
            <Route path="/models" element={<Models />} />
            <Route path="/nodes" element={<Nodes />} />
            <Route path="/deployments" element={<Deployments />} />
            <Route path="/scheduling" element={<Scheduling />} />
          </Routes>
        </MainLayout>
      </Layout>
    </Router>
  );
};

export default App;