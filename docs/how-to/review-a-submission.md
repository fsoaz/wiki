# Review a submission

Walk the contributor-to-reviewer loop on the seeded `quantum-computing` article.

You need both the API and the website running. See [Get the MVP running](../tutorials/getting-started.md).

## 1. Submit as a contributor

1. Open `http://localhost:3000/signin`.
2. Choose **Continue as Contributor**.
3. Open `http://localhost:3000/articles/quantum-computing`.
4. Use the article-page form to submit an improvement, for example a correction that says to clarify error-correction overhead.

The website calls `POST /api/v1/articles/{slug}/suggestions`. Every submission creates a [review queue](../glossary.md#review-queue) item.

You can also submit from curl after you obtain a contributor token ([sign in](sign-in-and-roles.md)):

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"contributor@example.com"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

curl -s -X POST http://localhost:8000/api/v1/articles/quantum-computing/suggestions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"suggestion_type":"correction","summary":"Clarify error-correction overhead.","proposed_text":"Add a sentence about error-correction overhead."}'
```

Open `/contributors` while still signed in as the contributor to see submission status.

## 2. Sign in as a reviewer

Sign out from `/signin` (**Clear local session**), then choose **Continue as Reviewer**.

Open `http://localhost:3000/review`. Filter by status or subject type if the queue is long.

## 3. Assign and decide

1. Assign the item to yourself from the reviewer dashboard.
2. Approve or reject it. Add a decision note.

Those actions call:

- `POST /api/v1/reviews/queue/{queue_item_id}/assign`
- `POST /api/v1/reviews/queue/{queue_item_id}/decision` with `{"decision":"approved"}` or `{"decision":"rejected"}`

## 4. Inspect the audit trail as admin

Sign in as `admin@example.com` and open `/admin`. You should see recent audit events for the submission, assignment, and decision, plus active sessions.

## Failure modes

- Submitting without a contributor session returns `401` or sends you back to sign-in.
- A blank or whitespace-only summary is rejected client- and server-side (`422`); so is text past the field's maximum length.
- A contributor token cannot load `/review` APIs (`403` `Reviewer access required`).
- An unknown queue id returns `404` `Queue item not found`.
- Deciding an already-decided or differently assigned item returns `409`. Reviewers cannot decide their own submissions (`403`). Decisions are final — there is no undo.
- The website does not raise a rich error when a mutation fails. If the queue does not change, check that the API is running and that you are signed in as the expected role.
