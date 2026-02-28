import React from "react";
import { ApprovalPanel } from "../components/ApprovalPanel";
import { LiveDesktopStream } from "../components/LiveDesktopStream";

export default function Page() {
  return (
    <main>
      <h1>SkyAgentOS Dashboard</h1>
      <ApprovalPanel />
      <LiveDesktopStream />
    </main>
  );
}
