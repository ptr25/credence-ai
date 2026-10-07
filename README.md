# Credence AI — AI-Based Digital Certificate Tamper Detection and Verification System

University AI course project, IIIT Kottayam. CSE311 · Semester 5, Batch 2.

## Team
- Pranathi TR — 2024BCS0069
- Rupasri M — 2024BCS0077
- Peswika Bavagni — 2024BCS0257
- Challa vidya — 2024BCS0157

Faculty: Prajeesh Sir

## Project reports
- [Concise illustrated report (PDF)](docs/reports/Credence_AI_Simple_Report.pdf)
- [Concise report (Word)](docs/reports/Credence_AI_Simple_Report.docx)
- [Detailed report (PDF)](docs/reports/Credence_AI_Project_Report.pdf)
- [Detailed report (Word)](docs/reports/Credence_AI_Project_Report.docx)

## Abstract
Digital academic certificates are vulnerable to unauthorized content changes, while conventional file hashes also flag harmless compression and re-exporting. Credence AI investigates visual certificate comparison using transfer learning and multi-signal classification. A pretrained ImageNet ResNet18 transforms each registered certificate and submitted document into a normalized 512-dimensional global embedding. Nine corresponding page regions provide local embeddings, improving sensitivity to changes that occupy only a small part of the document. Cosine similarities are combined with structural similarity and mean absolute pixel difference to form five classification features. Logistic regression and random forest are trained on automatically generated original–candidate pairs representing harmless transformations and deliberate visual alterations. Base certificates are separated across training, validation and test partitions to reduce leakage. Validation F1 selects the classifier, and held-out accuracy, precision, recall, F1 and ROC-AUC quantify performance. A FastAPI service and Next.js interface support issuance, document upload, visual difference maps, revocation and evaluation displays. SHA-256, a QR registry link and an LSB identity prototype complement the visual analysis. The system demonstrates why visual consistency can survive byte-level change, while explicitly limiting its claims to comparisons with a trusted reference and evaluation on a synthetic certificate template.

## Problem statement and objectives
Hash mismatch cannot distinguish benign re-encoding from credential editing. Build real neural fingerprints; detect important alterations; tolerate harmless transformations; combine global, local and structural features; measure classification performance; expose a usable verification workflow.

## System architecture
Next.js / TypeScript / Tailwind → FastAPI → Credence Vision + certificate services → SQLite and CredenceVault local storage. PyTorch ResNet18 supplies deep features, scikit-learn supplies classification, PyMuPDF and Pillow handle images, ReportLab generates PDFs. No blockchain or IPFS is used.

## AI methodology
- First page rendered to RGB and a fixed 900 × 636 canvas; portrait inputs rotate to landscape. Single-page documents only. No perspective or translation registration is currently implemented.
- Shared ImageNet preprocessing runs on the full image and each of nine 3 × 3 patches. The cached ResNet18 is in evaluation mode with inference mode enabled; FC is replaced by Identity. Every 512-vector is L2 normalized.
- Feature vector: global cosine, average patch cosine, minimum patch cosine, SSIM, normalized mean absolute pixel difference.
- Logistic regression (standardized inputs) and random forest compete on validation F1. The winning model is saved with joblib. Probabilities are estimator outputs, not fabricated or independently calibrated confidence guarantees.
- A predicted tampered document triggers suspicion; an authentic prediction plus changed SHA triggers transformed copy. Low confidence requests review. Registry revocation overrides visual results.

## Dataset generation, training and evaluation
36 base certificates × 15 variants = 540 pairs. Eight authentic variants: original, JPEG, resized, PDF re-render, blur, brightness, contrast and noise. Seven alterations: grade, name, course, ID, covered text, inserted text and removed region. Seed 42; 24/6/6 base certificates in train/validation/test (360/90/90 pairs). No variant of a base crosses partitions. See `backend/app/results/dataset.json` for feature-level metadata and labels. Candidate images are regenerated deterministically rather than stored individually.

```sh
PYTHONPATH=backend MPLCONFIGDIR="$PWD/backend/app/results/mpl" .venv/bin/python -m app.ai.train_classifier
```

Held-out results: accuracy **100%**, precision **100%**, recall **100%**, F1 **1.00**, ROC-AUC **1.00**, on 90 synthetic test pairs. Global-only accuracy: **81.11%**. These are measured template-specific results, not guarantees for real-world certificates.

`backend/app/results/metrics.json` contains actual results and feature ablations. The dashboard displays confusion matrix, ROC curve, feature distributions and model comparison. Positive class: tampered. Precision measures alert correctness, recall measures detection coverage, F1 combines both. Test size is small, and related layouts still limit generalization despite grouping.

## Application features
Hashed-password demo login; safely incremented certificate IDs in SQLite transactions; professional PDF with QR; SHA-256 of finalized bytes; persisted global and patch vectors; original/transformed/tampered demonstration through actual inference; upload PDF/PNG/JPEG; difference overlays; verification history; analytics; required-reason revocation; research/viva guide.

CredenceID Prototype stores `certificateID|checksum` in image least-significant bits. It is deliberately fragile and unkeyed: resizing or JPEG can remove it. It is an identity convenience, not proof against forgery. Enter the certificate ID when verifying transformed copies. The QR opens the public portal with the ID, and users upload the file for visual analysis.

## Installation and running
Python 3.9+ and Node 22 tested. Install the dependencies below. ImageNet pretrained weights download automatically on first use; internet access is required.

```sh
git clone https://github.com/ptr25/credence-ai.git
cd credence-ai
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend
npm ci
cd ..
# Train once if model files are absent:
PYTHONPATH=backend MPLCONFIGDIR="$PWD/backend/app/results/mpl" .venv/bin/python -m app.ai.train_classifier
# Terminal 1:
./start-backend.sh
# Terminal 2:
cd credence-ai/frontend
npm run dev
```

Open http://localhost:3000. API docs: http://localhost:8000/docs. Change `NEXT_PUBLIC_API_URL` if backend address changes. Services bind to loopback for the local demo.

Demo login: **admin@iiitk.ac.in / credence123**. Password uses PBKDF2-SHA256; sessions are random tokens, expire after eight hours, and reset with server restart.

## Three-minute faculty demo
1. Sign in, show dashboard engine status and pretrained ResNet18 description.
2. Issue Aarav Sharma's default certificate. Open/download the PDF.
3. Verify original; show SHA match, real CNN/patch similarity, SSIM and classifier probability.
4. Create and verify transformed copy; download the file and show changed SHA with visual consistency.
5. Create and verify tampered copy; show classifier decision, anomalous patch and difference map.
6. Open Credence Vision; show grouped test metrics, confusion matrix, ROC and ablation results.
7. Optionally revoke from Certificates with a reason, verify original again, and show REVOKED.

## API
`POST /api/auth/login`; `POST /api/certificates/issue`; `GET /api/certificates`; `GET /api/certificates/{id}`; `GET /api/certificates/{id}/download`; `POST /api/certificates/{id}/revoke`; `POST /api/verify` (multipart file and certificateId); `GET /api/verifications`; `GET /api/ai/status`; `GET /api/ai/metrics`; `GET /api/analytics`; `POST /api/demo/{id}/transform`; `POST /api/demo/{id}/tamper`.

Issue/list/history/analytics/demo/revoke require bearer login token. Read-only certificate metadata, PDFs and results are public for this course demo. Do not use this public storage arrangement for sensitive production student records.

## Validation
```sh
PYTHONPATH=backend .venv/bin/pytest -q
cd frontend
npm run build
```
The integration test checks login, unique IDs, SHA, watermark recovery, embedding shape and normalization, patches, cosine comparison, classifier loading, issuance/download, all three real inference paths, difference-map delivery and revocation precedence.

## Interface design
The interface uses warm ivory, cream (`#FAE6A5`), golden yellow (`#F2A900`), burnt orange (`#CC7100`) and deep brown (`#4C2800`). Locally bundled Barlow Condensed supplies the large display headlines, Space Grotesk supplies interface text, and IBM Plex Mono supplies technical labels. No external font service is required at runtime.

Responsive layouts include a collapsible phone navigation, searchable certificate registry, result filters, live issuance preview, visual verification report and matching evaluation plots. Updated screenshots: [dashboard](docs/screenshots/redesign-dashboard.jpg), [landing page](docs/screenshots/redesign-landing.jpg), [verification](docs/screenshots/redesign-verification.jpg), and [mobile](docs/screenshots/redesign-mobile.jpg).

## Screenshots and results
Evaluation figures are in `backend/app/results/` and displayed in Credence Vision. Original references and actual demo difference maps are in `backend/app/storage/`. Browser-verified screenshots: [Credence Vision](docs/screenshots/vision-dashboard.jpg) and [tampered certificate analysis](docs/screenshots/tamper-demo.jpg). See the application for the live dashboard and certificate preview.

Development uses `.next-dev` while production uses `.next`, so building does not corrupt a running demo.

## Limitations and future work
Synthetic variants and a single layout cannot establish real-world detection reliability. ImageNet features are not trained for semantic certificate text; tiny edits, skew, crops and adversarial alterations can evade detection. No OCR field comparison, perspective alignment or external institution authentication is implemented. Confidence is not calibrated, and perfect synthetic results must not be presented as universal accuracy. Hidden LSB data is lossy-transform fragile. Demo authentication and public local storage need production hardening.

Future work: larger independently sourced datasets, OCR semantic verification, Siamese networks, certificate-specific fine-tuning, adversarial evaluation, robust invisible watermarking, optional distributed storage and mobile verifier.

## Repository contents
The trained Random Forest, synthetic feature dataset, evaluation results, source and reports are included. The local registry and generated certificates are excluded; start the app and issue a certificate to create a fresh demo. Dependency folders and the pretrained-weight cache are excluded.

AI-assisted tools supported implementation, debugging, interface development and documentation.
