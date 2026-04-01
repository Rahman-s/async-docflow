"use client";

import { use, useEffect, useState } from "react";
import axios from "axios";
import Link from "next/link";

type Doc = {
  id: number;
  filename: string;
  status: string;
  progress: number;
  extracted_data: string | null;
  finalized_data: string | null;
  is_finalized: boolean;
  error_message: string | null;
};

export default function DocumentDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [doc, setDoc] = useState<Doc | null>(null);
  const [editedData, setEditedData] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchDoc = async () => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/documents/${id}`);
      setDoc(res.data);
      setEditedData(res.data.finalized_data || res.data.extracted_data || "");
    } catch (error) {
      console.error("Error fetching document:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoc();
  }, [id]);

  const saveReview = async () => {
    try {
      await axios.put(`http://127.0.0.1:8000/documents/${id}/review`, {
        finalized_data: editedData,
      });
      fetchDoc();
      alert("Review saved");
    } catch (error) {
      console.error("Error saving review:", error);
      alert("Review save failed");
    }
  };

  const finalize = async () => {
    try {
      await axios.put(`http://127.0.0.1:8000/documents/${id}/finalize`, {
        finalized_data: editedData,
      });
      fetchDoc();
      alert("Document finalized");
    } catch (error) {
      console.error("Error finalizing document:", error);
      alert("Finalize failed");
    }
  };

  const retry = async () => {
    try {
      await axios.post(`http://127.0.0.1:8000/documents/${id}/retry`);
      fetchDoc();
      alert("Retry started");
    } catch (error) {
      console.error("Error retrying document:", error);
      alert("Retry failed");
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!doc) return <div className="p-6">Document not found</div>;

  return (
    <main className="p-6 max-w-4xl mx-auto">
      <Link href="/" className="text-blue-600 underline">
        ← Back to Dashboard
      </Link>

      <h1 className="text-2xl font-bold mt-4 mb-4">{doc.filename}</h1>

      <div className="border rounded p-4 mb-4">
        <p><strong>Status:</strong> {doc.status}</p>
        <p><strong>Progress:</strong> {doc.progress}%</p>
        <p><strong>Finalized:</strong> {doc.is_finalized ? "Yes" : "No"}</p>
      </div>

      {doc.error_message && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {doc.error_message}
        </div>
      )}

      <label className="block mb-2 font-semibold">Review / Edit Output</label>

      <textarea
        value={editedData}
        onChange={(e) => setEditedData(e.target.value)}
        className="w-full h-80 border p-3 rounded mb-4 text-sm"
      />

      <div className="flex gap-3 flex-wrap">
        <button
          onClick={saveReview}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Save Review
        </button>

        <button
          onClick={finalize}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Finalize
        </button>

        {doc.status === "failed" && (
          <button
            onClick={retry}
            className="bg-red-600 text-white px-4 py-2 rounded"
          >
            Retry
          </button>
        )}
      </div>
    </main>
  );
}