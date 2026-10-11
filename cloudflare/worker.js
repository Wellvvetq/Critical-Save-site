/**
 * Critical Save Studio — Studio Control Center Edge Worker
 * Serverless Edge API for remote administration and GitHub Actions dispatch.
 * 
 * Free-tier Cloudflare Worker with D1 database binding and GitHub Webhook dispatch.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS Headers for API calls
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check
    if (path === "/api/health") {
      return new Response(JSON.stringify({
        status: "operational",
        studio: "Critical Save Studio",
        serverless_edge: true,
        timestamp: new Date().toISOString()
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    // List software releases telemetry
    if (path === "/api/releases" && request.method === "GET") {
      try {
        const { results } = await env.DB.prepare(
          "SELECT r.*, p.title_en as product_name FROM software_releases r JOIN software_products p ON r.product_id = p.id WHERE r.is_live = 1 ORDER BY r.created_at DESC"
        ).all();
        return new Response(JSON.stringify({ releases: results }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    // Trigger GitHub Actions workflow dispatch for remote static rebuild
    if (path === "/api/publish" && request.method === "POST") {
      // Validate Authorization header
      const authHeader = request.headers.get("Authorization");
      if (!env.ADMIN_API_KEY || authHeader !== `Bearer ${env.ADMIN_API_KEY}`) {
        return new Response(JSON.stringify({ error: "Unauthorized" }), {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      // If GITHUB_PAT and GITHUB_REPO are set, trigger repository dispatch
      if (env.GITHUB_PAT && env.GITHUB_REPO) {
        try {
          const ghRes = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
            method: "POST",
            headers: {
              "Accept": "application/vnd.github.v3+json",
              "Authorization": `token ${env.GITHUB_PAT}`,
              "User-Agent": "Critical-Save-Control-Center"
            },
            body: JSON.stringify({ event_type: "publish_static_site" })
          });

          if (ghRes.ok) {
            return new Response(JSON.stringify({
              status: "dispatched",
              message: "GitHub Actions static rebuild dispatched successfully."
            }), {
              headers: { ...corsHeaders, "Content-Type": "application/json" }
            });
          } else {
            const errText = await ghRes.text();
            return new Response(JSON.stringify({ error: "GitHub dispatch failed", details: errText }), {
              status: 502,
              headers: { ...corsHeaders, "Content-Type": "application/json" }
            });
          }
        } catch (e) {
          return new Response(JSON.stringify({ error: e.message }), {
            status: 500,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          });
        }
      }

      return new Response(JSON.stringify({
        status: "acknowledged",
        message: "Remote publishing signal received. Configure GITHUB_PAT to enable automated repository dispatch."
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    return new Response(JSON.stringify({
      name: "Critical Save Studio — Edge Control Center",
      routes: ["/api/health", "/api/releases", "/api/publish"]
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
};
