"use client";

import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import Link from "next/link";

type DocumentItem = {
  id: number;
  filename: string;
  status: string;
  progress: number;
};

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/documents", {
        params: { search, status },
      });
      setDocuments(res.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  }, [search, status]);

  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 2000);
    return () => clearInterval(interval);
  }, [fetchDocuments]);

  const handleUpload = async () => {
    if (!files) return;

    try {
      const formData = new FormData();

      Array.from(files).forEach((file) => {
        formData.append("files", file);
      });

      await axios.post("http://127.0.0.1:8000/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      fetchDocuments();
      alert("Upload successful");
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed");
    }
  };

  return (
    <main className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Async Document Workflow</h1>

      <div className="border p-4 rounded mb-6">
        <h2 className="text-xl font-semibold mb-3">Upload Documents</h2>

        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          className="mb-3"
        />

        <br />

        <button
          onClick={handleUpload}
          className="bg-black text-white px-4 py-2 rounded"
        >
          Upload
        </button>
      </div>

      <div className="flex gap-3 mb-6">
        <button
          onClick={() => window.open("http://127.0.0.1:8000/export/json", "_blank")}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Export JSON
        </button>

        <button
          onClick={() => window.open("http://127.0.0.1:8000/export/csv", "_blank")}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Export CSV
        </button>
      </div>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Search by filename"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border px-3 py-2 rounded w-full"
        />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border px-3 py-2 rounded"
        >
          <option value="">All</option>
          <option value="queued">Queued</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div className="space-y-3">
        {documents.map((doc) => (
          <div key={doc.id} className="border p-4 rounded">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold">{doc.filename}</p>
                <p className="text-sm text-gray-600">
                  {doc.status} - {doc.progress}%
                </p>
              </div>

              <Link
                href={`/documents/${doc.id}`}
                className="underline text-blue-600"
              >
                View Details
              </Link>
            </div>

            <div className="w-full bg-gray-200 h-3 rounded mt-2">
              <div
                className="bg-black h-3 rounded"
                style={{ width: `${doc.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}