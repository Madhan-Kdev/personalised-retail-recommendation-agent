import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import PersonaSwitcher from './components/PersonaSwitcher';
import CustomerStorefront from './components/CustomerStorefront';
import ConversationalAssistant from './components/ConversationalAssistant';
import GovernanceDashboard from './components/GovernanceDashboard';
import ModelBenchmarks from './components/ModelBenchmarks';
import RealtimeTelemetry from './components/RealtimeTelemetry';
import ProductDetailDrawer from './components/ProductDetailDrawer';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('storefront');
  const [customers, setCustomers] = useState([]);
  const [activeCustomer, setActiveCustomer] = useState(null);
  const [personaSynthesis, setPersonaSynthesis] = useState(null);
  const [allProducts, setAllProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [seasonalSignals, setSeasonalSignals] = useState(null);
  const [currentSeason, setCurrentSeason] = useState('Winter');
  const [selectedModel, setSelectedModel] = useState('hybrid');
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [healthStatus, setHealthStatus] = useState(true);

  // New Redesign States
  const [showConcierge, setShowConcierge] = useState(true);
  const [activeProductDetail, setActiveProductDetail] = useState(null);
  const [aiSearchSpotlight, setAiSearchSpotlight] = useState(null);

  // Chat History States
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Initial Data Fetch
  useEffect(() => {
    async function init() {
      try {
        const [custRes, prodRes, seasonRes] = await Promise.all([
          api.getCustomers(),
          api.getProducts(),
          api.getSeasonalSignals()
        ]);
        setCustomers(custRes);
        setAllProducts(prodRes);
        setSeasonalSignals(seasonRes);

        if (custRes.length > 0) {
          setActiveCustomer(custRes[0]);
        }
      } catch (err) {
        console.error("Initialization error:", err);
        setHealthStatus(false);
      }
    }
    init();
  }, []);

  // Fetch Recommendations & Persona Synthesis when Active Customer, Season, or Model changes
  const fetchRecsForActiveCustomer = async () => {
    if (!activeCustomer) return;
    setLoadingRecs(true);
    try {
      const [recData, profileData] = await Promise.all([
        api.getRecommendations(activeCustomer.id, currentSeason, selectedModel, 6),
        api.getCustomerProfile(activeCustomer.id)
      ]);
      setRecommendations(recData.recommendations || []);
      setPersonaSynthesis(profileData.persona_synthesis || null);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoadingRecs(false);
    }
  };

  useEffect(() => {
    if (activeCustomer) {
      fetchRecsForActiveCustomer();
      // Initialize chat greetings
      setChatMessages([
        {
          role: 'assistant',
          content: `Hello ${activeCustomer.name}! I am your AI concierge. I can find products matching your needs, compare details, explain specifications, or run budget inquiries.\n\nWhat can I help you find today?`,
          suggested_products: [],
          suggested_followups: [
            'Why did you recommend the top item for me?',
            'Find me running/fitness gear under $100',
            'Compare the top 2 recommended products'
          ]
        }
      ]);
      setAiSearchSpotlight(null);
    }
  }, [activeCustomer?.id, currentSeason, selectedModel]);

  // Handle Real-Time Customer Telemetry
  const handleInteraction = async (customerId, productId, eventType, rating = null) => {
    try {
      await api.recordInteraction(customerId, productId, eventType, rating);
      // Refresh customer data
      const updatedProfile = await api.getCustomerProfile(customerId);
      setActiveCustomer(updatedProfile.profile);

      // Update customers list
      setCustomers((prev) =>
        prev.map((c) => (c.id === customerId ? updatedProfile.profile : c))
      );

      // Re-fetch recommendations
      const recData = await api.getRecommendations(customerId, currentSeason, selectedModel, 6);
      setRecommendations(recData.recommendations || []);
      setPersonaSynthesis(updatedProfile.persona_synthesis || null);
    } catch (err) {
      console.error("Error logging interaction:", err);
    }
  };

  // Unified Natural Language Search Pipeline
  const handleSearchSubmit = async (query) => {
    if (!query) return;
    setChatLoading(true);
    try {
      const response = await api.sendChatMessage(activeCustomer.id, query, chatMessages.map(m => ({ role: m.role, content: m.content })));
      const resultObj = {
        query,
        reply: response.reply,
        suggested_products: response.suggested_products || [],
        suggested_followups: response.suggested_followups || []
      };

      setAiSearchSpotlight(resultObj);

      // Push to chat pane history
      setChatMessages((prev) => [
        ...prev,
        { role: 'user', content: query },
        {
          role: 'assistant',
          content: response.reply,
          suggested_products: response.suggested_products || [],
          suggested_followups: response.suggested_followups || []
        }
      ]);

      // Open the Concierge sidebar if it was closed
      setShowConcierge(true);
    } catch (err) {
      console.error("Search integration error:", err);
    } finally {
      setChatLoading(false);
    }
  };

  // Chat Pane Send Message Action
  const handleSendChatMessage = async (textToSend = null) => {
    const query = textToSend || chatInput.trim();
    if (!query || chatLoading) return;

    const userMsg = { role: 'user', content: query };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await api.sendChatMessage(activeCustomer.id, query, chatMessages.map(m => ({ role: m.role, content: m.content })));
      const botMsg = {
        role: 'assistant',
        content: response.reply,
        suggested_products: response.suggested_products || [],
        suggested_followups: response.suggested_followups || []
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error connecting to recommendations engine.',
          suggested_products: [],
          suggested_followups: []
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col justify-between selection:bg-zinc-100 selection:text-zinc-950">
      <div>
        {/* Top Navbar */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          customers={customers}
          activeCustomer={activeCustomer}
          onSelectCustomer={(c) => setActiveCustomer(c)}
          showConcierge={showConcierge}
          setShowConcierge={setShowConcierge}
        />

        {/* Main Content Layout */}
        <div className="flex flex-col lg:flex-row max-w-7xl mx-auto px-4 lg:px-8 py-6 gap-6 items-stretch">
          {/* Main Workspace (Left) */}
          <main className="flex-1 min-w-0">
            {activeTab === 'storefront' && (
              <CustomerStorefront
                activeCustomer={activeCustomer}
                recommendations={recommendations}
                allProducts={allProducts}
                seasonalSignals={seasonalSignals}
                currentSeason={currentSeason}
                selectedModel={selectedModel}
                setSelectedModel={setSelectedModel}
                onInteract={handleInteraction}
                onRefreshRecs={fetchRecsForActiveCustomer}
                loadingRecs={loadingRecs}
                onSearchSubmit={handleSearchSubmit}
                searchSpotlight={aiSearchSpotlight}
                setSearchSpotlight={setAiSearchSpotlight}
                onViewDetails={(prod) => setActiveProductDetail(prod)}
              />
            )}

            {activeTab === 'governance' && (
              <GovernanceDashboard />
            )}

            {activeTab === 'benchmarks' && (
              <ModelBenchmarks />
            )}
          </main>

          {/* AI Sidebar Concierge Dock (Right 1/3) */}
          {showConcierge && activeCustomer && (
            <aside className="w-full lg:w-80 shrink-0 flex flex-col gap-4 animate-slideIn">
              {/* Persona Narrative Summary Profile Widget */}
              <PersonaSwitcher
                activeCustomer={activeCustomer}
                personaSynthesis={personaSynthesis}
              />

              {/* Concierge Chat Widget */}
              <div className="flex-1 min-h-[400px] border border-zinc-850 rounded overflow-hidden">
                <ConversationalAssistant
                  activeCustomer={activeCustomer}
                  onInteract={handleInteraction}
                  messages={chatMessages}
                  setMessages={setChatMessages}
                  loading={chatLoading}
                  handleSend={handleSendChatMessage}
                  input={chatInput}
                  setInput={setChatInput}
                />
              </div>
            </aside>
          )}
        </div>
      </div>

      {/* Floating Session Telemetry Footer */}
      <footer className="sticky bottom-0 z-40">
        <RealtimeTelemetry customer={activeCustomer} onInteract={handleInteraction} />
      </footer>

      {/* Immersive Product Detail View Drawer */}
      {activeProductDetail && (
        <>
          <div
            className="fixed inset-0 bg-zinc-950/70 backdrop-blur-sm z-40 transition-opacity"
            onClick={() => setActiveProductDetail(null)}
          />
          <ProductDetailDrawer
            product={activeProductDetail}
            customer={activeCustomer}
            onClose={() => setActiveProductDetail(null)}
            onInteract={(custId, prodId, eventType) => {
              handleInteraction(custId, prodId, eventType);
              setActiveProductDetail(null);
            }}
          />
        </>
      )}
    </div>
  );
}
