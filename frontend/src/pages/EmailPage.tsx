//EmailPage.tsx
//This is responsible for displaying the full detail of a single email.

import { useParams } from 'react-router-dom';
import { useEmailDetail } from '../hooks/useEmailDetail';
import EmailDetail from '../components/EmailDetail';

//This page extracts the provider and id from the URL using useParams().
//It passes them to useEmailDetail() which fetches the full email data.
//The result is passed to EmailDetail for rendering.
export default function EmailPage() {
  const { provider, id } = useParams<{ provider: string; id: string }>();

  const { email, loading, error } = useEmailDetail(provider || '', id || '');

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!email) return <p>Email not found.</p>;

  return <EmailDetail email={email} />;
}
