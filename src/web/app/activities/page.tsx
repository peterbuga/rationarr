"use client";

import { AppSidebar } from "@/components/app-sidebar";
import { DataTable } from "@/components/data-table-activities";
import { SiteHeader } from "@/components/site-header";
import useSWR from "swr";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

const fetcher = async (url: string) => {
  const res = await fetch(url);
  return res.json();
};

export default function Page() {
  const { data, isLoading } = useSWR(`/api/activity`, fetcher, {
    refreshWhenOffline: false,
    revalidateOnFocus: false,
  });

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Activities" />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              {!isLoading && <DataTable data={data} />}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
