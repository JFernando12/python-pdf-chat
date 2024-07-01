import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PdfViewerProps {
  file: string;
  className?: string;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ file, className }) => {
  return (
    <div className={className}>
      <embed src={file} type="application/pdf" width="100%" height="100%" />
    </div>
  );
};

export default PdfViewer;
