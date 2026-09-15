# CogniTree: Project Completion Status and Development Plan

## 1. Project Title

**AI-Powered Diagnostic Study System (CogniTree)**

## 2. Project Objective

CogniTree is an adaptive learning platform that converts textbooks and course materials into grounded multiple-choice assessments. It records student responses, identifies weaknesses at a fine-grained concept and cognitive-skill level, and generates targeted remediation quizzes.

The core research question is:

> Can repeated, multidimensional assessment and fine-grained topic-level analysis accurately isolate a student's persistent cognitive gaps and guide personalized practice?

## 3. Features Currently Implemented

The current prototype includes the following functional components:

### 3.1 User Authentication

- User signup and login
- Password hashing
- JWT-based authenticated sessions
- Protected backend endpoints

### 3.2 Document Ingestion

- PDF and text-document upload
- Text extraction from uploaded material
- Text chunking with overlap
- Persistent storage of extracted chunks
- ChromaDB and local SQLite retrieval support
- Document ingestion status tracking

### 3.3 LLM Question Generation

- Gemini API integration
- Configurable Gemini model
- API/model health check
- JSON response enforcement
- Pydantic question validation
- Rejection of invalid output
- No heuristic or fabricated fallback questions
- Batch generation to reduce API usage
- Quota-aware error handling
- Balanced generation of multiple questions for concept tags

### 3.4 Quiz Engine

- General, topic-specific and document-specific quizzes
- Configurable quiz length
- Answer submission and validation
- Response-time recording
- Final scores and accuracy
- Wrong-answer review and explanations
- Balanced selection across available subtopic and skill cells

### 3.5 Diagnostic Analytics

- Aggregation by topic, subtopic and cognitive skill
- Minimum evidence requirement before labelling mastery or weakness
- Accuracy and attempt counts
- Mastered, weak and insufficient-evidence states
- Fine-grained weakness display in the dashboard

### 3.6 Adaptive Remediation

- Identification of weak diagnostic cells
- Selection of questions matching the weak topic, subtopic and skill
- Prioritization of unseen questions
- Adaptive remediation quiz sessions

## 4. Estimated Current Completion

Relative to the complete proposed architecture, the project is approximately **50–55% complete as a functional capstone prototype**.

This estimate is based on the fact that all five major pipeline modules have basic working implementations:

1. Document ingestion
2. Question generation
3. Quiz delivery
4. Diagnostic analytics
5. Adaptive remediation

However, several research-quality and production-quality elements remain incomplete. The current system demonstrates the complete idea, but the taxonomy, question governance, cognitive model, testing and evaluation methodology still need development.

## 5. Minimum Work Required for a 50–60% Teacher Demonstration

To present the project credibly at approximately 50–60% completion, the following features should be completed next.

### Priority 1: Canonical Concept Tags

Create a persistent `ConceptTag` table and connect questions to immutable tag IDs.

Minimum required functionality:

- Store canonical tag name and definition
- Normalize tag names
- Reuse exact tag-name matches
- Store aliases such as "scanner" for "lexical analysis"
- Connect textbook evidence to tags
- Prevent similar names from becoming duplicate diagnostic categories

Expected demonstration:

> Two textbooks that discuss lexical analysis are connected to the same canonical concept tag.

### Priority 2: Four Cognitive Skill Dimensions

Replace the current two categories with the four categories from the project proposal:

1. Recall
2. Conceptual understanding
3. Application
4. Problem-solving

Generate at least two questions per concept and cognitive skill.

Recommended minimum coverage:

| Concept Tag | Recall | Conceptual | Application | Problem-Solving |
|---|---:|---:|---:|---:|
| Lexical Analysis | 2 | 2 | 2 | 2 |

This produces eight questions per concept tag, which is sufficient for a prototype demonstration.

### Priority 3: Source Provenance

Every generated question should store:

- Source document ID
- Source chunk index
- Supporting quotation or excerpt
- Generation model
- Generation timestamp

This allows the teacher or reviewer to confirm that a question is grounded in the uploaded material.

### Priority 4: Minimal Tag Review Workflow

Add a basic proposed-tag screen with three actions:

- Approve
- Reject
- Merge with an existing tag

A sophisticated administration panel is not required for the 50–60% milestone. A simple table or card interface is sufficient.

### Priority 5: Automated Tests

Add a small but meaningful test suite covering:

- Question-schema validation
- Batch question balance
- Exact tag reuse
- Alias matching
- Diagnostic grouping
- Minimum-evidence rules
- Adaptive selection of weak tags

Approximately 10–15 focused automated tests would be sufficient for the interim demonstration.

### Priority 6: Demonstration Dataset and Scenario

Prepare one controlled end-to-end demonstration using a Compiler Design textbook or chapter.

Recommended demonstration sequence:

1. Upload the Compiler Design material.
2. Show extracted concept tags.
3. Generate questions for three or four tags.
4. Take a diagnostic quiz using a test student.
5. Intentionally answer questions from one tag incorrectly.
6. Show the weakness matrix identifying that tag and skill.
7. Launch the adaptive remediation quiz.

## 6. Features That Can Be Deferred

The following features are valuable but are not necessary for a 50–60% completion presentation:

- Full three-level difficulty calibration
- Item Response Theory
- Bayesian Knowledge Tracing
- Advanced confidence intervals
- Large-scale teacher administration system
- Complete audit-log interface
- Celery or another distributed task queue
- Production PostgreSQL deployment
- Comprehensive OCR system
- Multi-school or multi-classroom support
- Fine-grained institutional permissions
- Automated psychometric question analysis
- Full cloud deployment and monitoring

These can be presented as future work.

## 7. Recommended Simplified Development Plan

### Stage 1: Canonical Taxonomy

- Add `ConceptTag`, `TagAlias` and `DocumentTagEvidence`
- Add `tag_id` to questions
- Convert existing subtopics into canonical tags
- Implement exact-name and alias matching
- Allow Gemini to propose reuse or creation

### Stage 2: Tag-Based Assessment

- Add four cognitive skills
- Generate two questions per tag and skill
- Store source provenance
- Aggregate diagnostics by `tag_id` and skill
- Update adaptive remediation to use canonical tag IDs

### Stage 3: Review and Verification

- Add the minimal tag-review screen
- Add automated tests
- Prepare the controlled Compiler Design demonstration
- Document current limitations and future work

## 8. Suggested 60% Completion Definition

CogniTree can reasonably be described as 60% complete when it can demonstrate this flow reliably:

```text
Upload textbook
→ extract grounded concept tags
→ reuse or propose canonical tags
→ generate balanced questions across four skills
→ conduct a quiz
→ diagnose a precise weak tag and skill
→ launch targeted remediation
```

The system does not need to be production-ready at this stage. It must demonstrate that the central research idea works coherently with traceable data.

## 9. Estimated Remaining Work for the Interim Milestone

The recommended 50–60% milestone requires approximately **five major deliverables**:

1. Canonical concept-tag storage and reuse
2. Four cognitive skill dimensions
3. Question source provenance
4. Minimal tag approval and merge workflow
5. Automated tests and a controlled demonstration scenario

Depending on implementation speed and familiarity with database migrations, this is approximately **one to two focused development weeks** for a functional capstone prototype. This estimate does not include production deployment or a formal student research study.

## 10. Presentation Positioning

The project should be presented as a working research prototype rather than a completed commercial platform.

Suggested statement:

> The current CogniTree prototype implements the complete ingestion-to-remediation pipeline. The next development milestone focuses on stabilizing the curriculum taxonomy, expanding cognitive-skill coverage, adding source-level auditability and validating the diagnostic logic through controlled tests.

