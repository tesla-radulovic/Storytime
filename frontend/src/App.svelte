<script lang="ts">
  import { onMount } from 'svelte';

  type Rating = 'Too Easy' | 'Just Right' | 'Too Hard';
  let story = '';
  let loading = false;
  let error: string | null = null;
  let hasRated = false;

  const API_URL = 'http://localhost:8000';

  async function fetchStory(last_rating?: Rating) {
    loading = true;
    error = null;
    hasRated = false;
    try {
      const res = await fetch(`${API_URL}/generate_story`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ last_rating }),
      });
      if (!res.ok) throw new Error('Failed to fetch story');
      const data = await res.json();
      story = data.story;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  }

  function handleRating(rating: Rating) {
    hasRated = true;
    if (rating === 'Just Right') return;
    fetchStory(rating);
  }

  onMount(() => {
    fetchStory();
  });
</script>

<main style="max-width: 900px; margin: 0 auto; padding: 2rem 1rem; font-family: system-ui, sans-serif;">
  {#if loading}
    <p>Loading...</p>
  {:else if error}
    <p style="color: #c00;">{error}</p>
  {:else}
    <div style="white-space: pre-line; font-size: 1.2rem; color: #222; text-align: left; margin-bottom: 2rem;">
      {story}
    </div>
  {/if}
  <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
    <button
      on:click={() => handleRating('Too Easy')}
      disabled={loading || hasRated}
      style="padding: 0.6rem 1.2rem;"
    >Too Easy</button>
    <button
      on:click={() => handleRating('Just Right')}
      disabled={loading || hasRated}
      style="padding: 0.6rem 1.2rem;"
    >Just Right</button>
    <button
      on:click={() => handleRating('Too Hard')}
      disabled={loading || hasRated}
      style="padding: 0.6rem 1.2rem;"
    >Too Hard</button>
  </div>
  {#if hasRated}
    <p style="color: #3366cc;">Thank you for your feedback!</p>
  {/if}
</main>
