import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { SkeletonList } from "@/components/ui/Skeleton";
import { AppLayout } from "./layout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import ApplicationsList from "@/pages/ApplicationsList";
import ApplicationNew from "@/pages/ApplicationNew";
import ApplicationDetail from "@/pages/ApplicationDetail";
import ReviewQueue from "@/pages/ReviewQueue";
import ClientsList from "@/pages/ClientsList";
import ClientDetail from "@/pages/ClientDetail";
import Models from "@/pages/Models";
import Monitoring from "@/pages/Monitoring";
import Admin from "@/pages/Admin";

export function ProtectedRoute() {
  const { status } = useAuth();
  if (status === "idle" || status === "loading") {
    return <SkeletonList rows={6} variant="card" />;
  }
  if (status !== "authenticated") {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

export function PublicOnlyRoute() {
  const { status } = useAuth();
  if (status === "authenticated") {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}

export function AppRouter() {
  return (
    <Routes>
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<Login />} />
      </Route>
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/applications" element={<ApplicationsList />} />
          <Route path="/applications/new" element={<ApplicationNew />} />
          <Route path="/applications/:id" element={<ApplicationDetail />} />
          <Route path="/clients" element={<ClientsList />} />
          <Route path="/clients/:id" element={<ClientDetail />} />
          <Route path="/review" element={<ReviewQueue />} />
          <Route path="/models" element={<Models />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>
    </Routes>
  );
}
