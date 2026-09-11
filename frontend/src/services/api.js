export async function api(path, body) {
  const response = await fetch('/api' + path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: {'Content-Type': 'application/json'},
    ...(body === undefined ? {} : {body: JSON.stringify(body)}),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'APOLLO is unavailable. Please try again.');
  return data;
}
export const time = value => new Date(value).toLocaleString([], {dateStyle: 'medium', timeStyle: 'short'});
export const money = value => new Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR'}).format(value);

