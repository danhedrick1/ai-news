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
  const provider = process.env.BUTTONDOWN_API_KEY
    ? 'buttondown'
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
  const submittedAt = new Date().toISOString();

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'Enter a valid email address.' }, { status: 400 });
  }

  try {
    if (process.env.BUTTONDOWN_API_KEY) {
      const response = await fetch('https://api.buttondown.email/v1/subscribers', {
        method: 'POST',
        headers: {
          Authorization: `Token ${process.env.BUTTONDOWN_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_address: email,
          tags: ['the-bash'],
          metadata: {
            source,
            submitted_at: submittedAt,
          },
        }),
      });

      if (!response.ok) {
        const errorText = await safeErrorText(response);
        if (/already|exists|subscribed/i.test(errorText)) {
          return json({ ok: true, message: 'You are already subscribed.' });
        }
        return json(
          { ok: false, error: 'Could not add this address to Buttondown right now.' },
          { status: 502 }
        );
      }

      return json({ ok: true, message: 'You are on the list. Daily signal is on the way.' });
    }

    if (process.env.NEWSLETTER_WEBHOOK_URL) {
      const response = await fetch(process.env.NEWSLETTER_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          source,
          submittedAt,
          product: 'The Bash',
        }),
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
