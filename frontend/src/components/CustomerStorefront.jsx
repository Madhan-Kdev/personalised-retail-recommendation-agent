import React, { useState } from 'react';
import { Search, Compass, RefreshCw, Eye, ShoppingCart, Sparkles, AlertCircle, Trash2, ArrowRight } from 'lucide-react';
import RecommendationCard from './RecommendationCard';

export default function CustomerStorefront({
  activeCustomer,
  recommendations,
  allProducts,
  currentSeason,
  onInteract,
  onRefreshRecs,
  loadingRecs,
  onSearchSubmit,
  searchSpotlight,
  setSearchSpotlight,
  onViewDetails
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [activeCatalogTab, setActiveCatalogTab] = useState('recommendations'); // 'recommendations' or 'catalog'
  const [searching, setSearching] = useState(false);

  const categories = ['All', 'Electronics & Audio', 'Fitness & Outdoors', 'Apparel & Fashion', 'Home & Kitchen', 'Beauty & Skincare', 'Gourmet & Coffee'];

  const prompts = [
    { text: 'Compare top running shoes', query: 'Compare the top 2 recommended products' },
    { text: 'Find travel gear under $100', query: 'Find me running/fitness gear under $100' },
    { text: 'What is trending for Winter?', query: 'What is trending for Winter?' },
  ];

  const handlePromptClick = async (queryText) => {
    setSearchQuery(queryText);
    await handleSearch(queryText);
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    await handleSearch(searchQuery);
  };

  const handleSearch = async (queryText) => {
    setSearching(true);
    try {
      await onSearchSubmit(queryText);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const filteredCatalog = allProducts.filter((p) => {
    const matchesCat = selectedCategory === 'All' || p.category === selectedCategory;
    const matchesSearch = !searchQuery || p.title.toLowerCase().includes(searchQuery.toLowerCase()) || p.brand.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  // Spotlight is the first recommendation
  const spotlightRec = recommendations[0];
  const secondaryRecs = recommendations.slice(1, 3);
  const remainingRecs = recommendations.slice(3);

  return (
    <div className="space-y-12">
      {/* 1. AI Concierge Hero Search Section */}
      <section className="text-center py-10 max-w-3xl mx-auto space-y-6">
        <div className="space-y-2">
          <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-550">
            Intelligent Concierge
          </span>
          <h2 className="text-2xl sm:text-3xl font-light tracking-tight text-zinc-150">
            How can I assist your shopping today?
          </h2>
          <p className="text-xs text-zinc-450 leading-relaxed max-w-xl mx-auto">
            Describe your needs, budget, or preferences in natural language. Our AI concierge interprets requirements and synthesizes personalized suggestions.
          </p>
        </div>

        {/* Natural Language Input */}
        <form onSubmit={handleSearchSubmit} className="relative max-w-2xl mx-auto">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g., 'I need fitness gear under $100' or 'Recommend high-end electronics'..."
            className="w-full bg-zinc-900/60 text-zinc-200 text-xs rounded pl-11 pr-24 py-3.5 border border-zinc-850 focus:border-zinc-800 focus:outline-none transition-all shadow-sm"
          />
          <Search className="w-4 h-4 text-zinc-500 absolute left-4 top-1/2 -translate-y-1/2" />
          <button
            type="submit"
            disabled={searching || !searchQuery.trim()}
            className="absolute right-2 top-1.5 bottom-1.5 px-3 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 font-semibold text-[10px] transition-colors disabled:opacity-50"
          >
            {searching ? 'Parsing...' : 'Ask AI'}
          </button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center justify-center gap-1.5 text-[10px]">
          <span className="text-zinc-550 font-medium">Try asking:</span>
          {prompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handlePromptClick(p.query)}
              className="px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-zinc-200 border border-zinc-850/60 transition-colors"
            >
              {p.text}
            </button>
          ))}
        </div>
      </section>

      {/* 2. AI Shopping Spotlight Panel (Active Search Result Card) */}
      {searchSpotlight && (
        <section className="p-6 rounded bg-zinc-900 border border-zinc-850 max-w-5xl mx-auto space-y-6 relative animate-fadeIn">
          <button
            onClick={() => setSearchSpotlight(null)}
            className="absolute top-4 right-4 p-1 rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
            title="Clear Search"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          {/* Heading */}
          <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
            <Sparkles className="w-4.5 h-4.5 text-zinc-400" />
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
                AI Interpretation
              </h3>
              <p className="text-[10px] text-zinc-500 font-mono mt-0.5">Query: "{searchSpotlight.query}"</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 1/3: Rationale */}
            <div className="lg:col-span-1 space-y-4">
              <div className="space-y-1">
                <span className="text-[9px] uppercase font-bold text-zinc-550">Concierge Rationale</span>
                <p className="text-xs text-zinc-400 leading-relaxed font-normal">
                  {searchSpotlight.reply}
                </p>
              </div>

              {searchSpotlight.suggested_followups && searchSpotlight.suggested_followups.length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-zinc-850">
                  <span className="text-[9px] uppercase font-bold text-zinc-550">Follow-up Prompts</span>
                  <div className="space-y-1.5">
                    {searchSpotlight.suggested_followups.map((fol, idx) => (
                      <button
                        key={idx}
                        onClick={() => handlePromptClick(fol)}
                        className="w-full flex items-center justify-between p-2 rounded bg-zinc-950 hover:bg-zinc-850 text-left text-[11px] text-zinc-300 border border-zinc-850 transition-colors"
                      >
                        <span className="truncate">{fol}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-zinc-550" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right 2/3: Products Asymmetrical Grid */}
            <div className="lg:col-span-2 space-y-3">
              <span className="text-[9px] uppercase font-bold text-zinc-550 block">AI Matching Catalog Picks</span>
              {searchSpotlight.suggested_products && searchSpotlight.suggested_products.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {searchSpotlight.suggested_products.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => onViewDetails && onViewDetails(p)}
                      className="tactile-card rounded overflow-hidden flex items-center gap-4 p-3 cursor-pointer group"
                    >
                      <img src={p.image_url} alt="" className="w-16 h-16 rounded object-cover bg-zinc-950 shrink-0 border border-zinc-850" />
                      <div className="flex-1 min-w-0">
                        <span className="text-[9px] font-mono text-zinc-550 uppercase">{p.category}</span>
                        <h4 className="text-xs font-semibold text-zinc-200 truncate group-hover:text-zinc-100">{p.title}</h4>
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-xs font-bold text-zinc-100">${p.price.toFixed(2)}</span>
                          <span className="text-[10px] text-zinc-450 hover:text-zinc-200 flex items-center gap-1 font-semibold">
                            <span>View</span>
                            <ArrowRight className="w-3 h-3" />
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-zinc-950 border border-zinc-850 text-zinc-500 text-xs">
                  No direct products referenced in output.
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* 3. Navigation tabs for storefront feed vs explore */}
      <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
        <div className="flex items-center gap-1 p-1 bg-zinc-900/60 rounded border border-zinc-900">
          <button
            onClick={() => setActiveCatalogTab('recommendations')}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-all tactile-btn ${
              activeCatalogTab === 'recommendations'
                ? 'bg-zinc-100 text-zinc-950 font-semibold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Personalized Feed</span>
          </button>
          <button
            onClick={() => setActiveCatalogTab('catalog')}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-all tactile-btn ${
              activeCatalogTab === 'catalog'
                ? 'bg-zinc-100 text-zinc-950 font-semibold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Explore Catalog</span>
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onRefreshRecs}
            disabled={loadingRecs}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-350 border border-zinc-850 text-xs font-medium transition-colors disabled:opacity-50 tactile-btn"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingRecs ? 'animate-spin' : ''}`} />
            <span>Re-Rank Engine</span>
          </button>
        </div>
      </div>

      {/* 4. Display Grids */}
      {activeCatalogTab === 'recommendations' ? (
        <div className="space-y-10">
          {loadingRecs ? (
            <div className="flex flex-col items-center justify-center py-20">
              <RefreshCw className="w-6 h-6 text-zinc-400 animate-spin mb-2" />
              <p className="text-xs text-zinc-500 font-mono">Running multi-model inference...</p>
            </div>
          ) : recommendations.length > 0 ? (
            <div className="space-y-10">
              {/* Asymmetrical Editorial Layout */}
              {/* A. Spotlight Editorial Choice (Large Card) */}
              {spotlightRec && (
                <div className="space-y-3">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-550 block">AI Curated Choice</span>
                  <div
                    onClick={() => onViewDetails && onViewDetails(spotlightRec.product)}
                    className="tactile-card rounded overflow-hidden grid grid-cols-1 md:grid-cols-12 cursor-pointer group"
                  >
                    <div className="md:col-span-5 h-64 md:h-full bg-zinc-950 relative overflow-hidden border-r border-zinc-850">
                      <img src={spotlightRec.product.image_url} alt="" className="w-full h-full object-cover transition-transform group-hover:scale-103" />
                      <span className="absolute top-3 left-3 px-2 py-0.5 rounded bg-zinc-950/90 text-zinc-200 border border-zinc-800 text-[10px] font-mono">
                        Spotlight Recommendation
                      </span>
                    </div>

                    <div className="md:col-span-7 p-6 flex flex-col justify-between space-y-4">
                      <div>
                        <span className="text-[10px] font-mono text-zinc-500 uppercase">{spotlightRec.product.category}</span>
                        <h3 className="text-base font-semibold text-zinc-150 mt-1 leading-tight group-hover:text-zinc-100 transition-colors">
                          {spotlightRec.product.title}
                        </h3>
                        <p className="text-xs text-zinc-450 leading-relaxed mt-2">{spotlightRec.product.description}</p>
                      </div>

                      <div className="p-3 rounded bg-zinc-950 border border-zinc-850">
                        <p className="text-xs text-zinc-350 italic">
                          "{spotlightRec.explanation.headline_explanation}"
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-zinc-850 mt-2">
                        <span className="text-lg font-bold text-zinc-100">${spotlightRec.product.price.toFixed(2)}</span>
                        <span className="text-xs text-zinc-450 group-hover:text-zinc-200 flex items-center gap-1 font-semibold">
                          <span>Inspect details</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* B. Secondary Picks (Two-column layout) */}
              {secondaryRecs.length > 0 && (
                <div className="space-y-3">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-550 block">AI Recommended Pairing</span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {secondaryRecs.map((rec) => (
                      <RecommendationCard
                        key={rec.product.id}
                        rec={rec}
                        onInteract={onInteract}
                        activeCustomerId={activeCustomer?.id}
                        onViewDetails={onViewDetails}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* C. Long-tail Recommendations (Three-column layout) */}
              {remainingRecs.length > 0 && (
                <div className="space-y-3">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-550 block">Other High-Affinity Matches</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {remainingRecs.map((rec) => (
                      <RecommendationCard
                        key={rec.product.id}
                        rec={rec}
                        onInteract={onInteract}
                        activeCustomerId={activeCustomer?.id}
                        onViewDetails={onViewDetails}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-16 bg-zinc-900 border border-zinc-800 rounded p-6">
              <Compass className="w-8 h-8 text-zinc-500 mx-auto mb-2" />
              <p className="text-xs text-zinc-400 font-semibold">No recommendations found.</p>
            </div>
          )}
        </div>
      ) : (
        /* Full Catalog Explorer */
        <div className="space-y-6">
          {/* Category Filter Chips */}
          <div className="flex flex-wrap gap-1.5 pb-2 border-b border-zinc-900">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap transition-all tactile-btn ${
                  selectedCategory === cat
                    ? 'bg-zinc-100 text-zinc-950 font-semibold'
                    : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800/80'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Catalog grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {filteredCatalog.map((prod) => (
              <div
                key={prod.id}
                onClick={() => onViewDetails && onViewDetails(prod)}
                className="tactile-card rounded overflow-hidden flex flex-col justify-between group cursor-pointer"
              >
                <div>
                  <div className="relative h-40 w-full overflow-hidden bg-zinc-950">
                    <img src={prod.image_url} alt={prod.title} className="w-full h-full object-cover group-hover:scale-103 transition-transform" />
                    <span className="absolute bottom-2 left-2 text-xs font-mono font-bold text-zinc-100 bg-zinc-900/90 px-2 py-0.5 rounded border border-zinc-800">
                      ${prod.price.toFixed(2)}
                    </span>
                  </div>
                  <div className="p-3.5">
                    <div className="text-[9px] font-mono text-zinc-500 uppercase mb-1">{prod.category}</div>
                    <h4 className="text-xs font-semibold text-zinc-200 line-clamp-1 mb-1">{prod.title}</h4>
                    <p className="text-[11px] text-zinc-450 line-clamp-2 leading-relaxed">{prod.description}</p>
                  </div>
                </div>

                <div className="p-3.5 pt-0 border-t border-zinc-850/60 flex items-center gap-1.5 mt-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onViewDetails && onViewDetails(prod);
                    }}
                    className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded text-[11px] font-semibold bg-zinc-950 hover:bg-zinc-800 text-zinc-300 border border-zinc-850 transition-colors tactile-btn"
                  >
                    <Eye className="w-3.5 h-3.5 text-zinc-500" />
                    <span>Specs</span>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onInteract(activeCustomer?.id, prod.id, 'add_to_cart');
                    }}
                    className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded text-[11px] font-bold bg-zinc-100 hover:bg-zinc-200 text-zinc-950 transition-colors tactile-btn"
                  >
                    <ShoppingCart className="w-3.5 h-3.5 text-zinc-950" />
                    <span>Cart</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
