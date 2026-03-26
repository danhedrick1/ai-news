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
  const provider = process.env.BEEHIIV_API_KEY && process.env.BEEHIIV_PUBLICATION_ID
    ? 'beehiiv'
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

  // Map source tag to UTM fields
  let utmCampaign = 'site';
  if (source.startsWith('daily:')) utmCampaign = 'daily_digest';
  else if (source.startsWith('weekly:')) utmCampaign = 'weekly_recap';

  try {
    if (process.env.BEEHIIV_API_KEY && process.env.BEEHIIV_PUBLICATION_ID) {
      const url = `https://api.beehiiv.com/v2/publications/${process.env.BEEHIIV_PUBLICATION_ID}/subscriptions`;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${process.env.BEEHIIV_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          reactivate_existing: true,
          send_welcome_email: false, // handled by Beehiiv automation sequence
          utm_source: 'theba.sh',
          utm_medium: 'website',
          utm_campaign: utmCampaign,
          referring_site: 'theba.sh',
          custom_fields: [
            { name: 'source', value: source },
            { name: 'submitted_at', value: submittedAt },
          ],
        }),
      });

      if (!response.ok) {
        const errorText = await safeErrorText(response);
        // Beehiiv returns 400 with a message for already-subscribed when reactivate_existing is false.
        // With reactivate_existing: true it should always succeed for valid emails.
        if (response.status === 409 || /already|exists|subscribed/i.test(errorText)) {
          return json({ ok: true, message: 'You are already on the list.' });
        }
        console.error('Beehiiv API error', response.status, errorText);
        return json(
          { ok: false, error: 'Could not add this address right now. Try again in a moment.' },
          { status: 502 }
        );
      }

      return json({ ok: true, message: 'You are on the list. Check your inbox to confirm.' });
    }

    if (process.env.NEWSLETTER_WEBHOOK_URL) {
      const response = await fetch(process.env.NEWSLETTER_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, submittedAt, product: 'theba.sh' }),
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
