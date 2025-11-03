// src/components/layout/MainLayout/MainLayout.tsx
import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import Header from "../Header/Header";
import Sidebar from "../SideBar/SideBar";

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar pour mobile (overlay) */}
      <div
        className={`${
          sidebarOpen ? "block" : "hidden"
        } fixed inset-0 z-40 lg:hidden`}
      >
        <div
          className="fixed inset-0 bg-slate-900 bg-opacity-50"
          onClick={toggleSidebar}
          aria-hidden="true"
        ></div>
        <div className="relative flex flex-col w-72 max-w-xs h-full bg-white border-r">
          <Sidebar mobile onClose={toggleSidebar} />
        </div>
      </div>

      {/* Sidebar pour desktop (fixe) */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64">
          <Sidebar />
        </div>
      </div>

      {/* Contenu principal */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header onToggleSidebar={toggleSidebar} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
