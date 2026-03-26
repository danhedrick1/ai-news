const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function json(data, init = {}) {
  const headers = new Headers(init.headers || {});
  headers.set('content-type', 'application/json; charset=utf-8');
  headers.set('cache-control', 'no-store');
  return new Response(JSON.stringify(data), { ...init, headers });
}

async function safeErrorText(response) {
  try {
    return await response.text();
  } catch {
    return '';
  }
}

export async function GET() {
  const provider = process.env.KIT_API_KEY && process.env.KIT_FORM_ID
    ? 'kit'
    : process.env.NEWSLETTER_WEBHOOK_URL
      ? 'webhook'
      : 'unconfigured';

  return json({ ok: true, provider });
}

export async function POST(request) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: 'Invalid request body.' }, { status: 400 });
  }

  const email = String(body?.email || '').trim().toLowerCase();
  const source = String(body?.source || 'site').trim().slice(0, 64);

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'Enter a valid email address.' }, { status: 400 });
  }

  try {
    if (process.env.KIT_API_KEY && process.env.KIT_FORM_ID) {
      const url = `https://api.convertkit.com/v3/forms/${process.env.KIT_FORM_ID}/subscribe`;

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: process.env.KIT_API_KEY,
          email,
          fields: { source },
        }),
      });

      if (!response.ok) {
        const errorText = await safeErrorText(response);
        console.error('Kit API error', response.status, errorText);
        return json(
          { ok: false, error: 'Could not add this address right now. Try again in a moment.' },
          { status: 502 }
        );
      }

      // Kit returns 200 for both new and already-subscribed — no special case needed.
      return json({ ok: true, message: 'You are on the list. Check your inbox to confirm.' });
    }

    if (process.env.NEWSLETTER_WEBHOOK_URL) {
      const response = await fetch(process.env.NEWSLETTER_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, submittedAt: new Date().toISOString(), product: 'theba.sh' }),
      });

      if (!response.ok) {
        return json(
          { ok: false, error: 'The webhook did not accept the signup.' },
          { status: 502 }
        );
      }

      return json({ ok: true, message: 'Thanks. Your email was captured successfully.' });
    }

    return json(
      { ok: false, error: 'Newsletter delivery is not configured yet.' },
      { status: 503 }
    );
  } catch {
    return json(
      { ok: false, error: 'Something went wrong while sending the signup.' },
      { status: 500 }
    );
  }
}
