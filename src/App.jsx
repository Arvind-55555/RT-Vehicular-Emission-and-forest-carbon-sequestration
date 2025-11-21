import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, 
  doc, 
  setDoc, 
  onSnapshot, 
  getDoc 
} from 'firebase/firestore';
import { DollarSign, Truck, TreePine, BarChart2, Zap } from 'lucide-react';

// --- Global Context Variables from Canvas Environment ---
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? 
  JSON.parse(__firebase_config) : 
  {};
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

// --- Utility Functions ---

// Exponential backoff retry logic for fetch
const retryFetch = async (url, options, maxRetries = 5, delay = 1000) => {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        }
    }
};

const SIMULATION_DOC_PATH = `/artifacts/${appId}/public/data/carbon_tracker/data`;

// Initial state for the simulation (simplified coefficients for demonstration)
const initialConfig = {
    // Input parameters
    numVehicles: 5000, 
    forestAreaAcres: 1000, 
    // Simplified Rates (CO2 tons/year)
    co2PerVehicleFactor: 4.5, // 4.5 tons CO2/vehicle/year (e.g., typical sedan)
    sequestrationPerAcreRate: 3.6, // 3.6 tons CO2/acre/year (e.g., average US forest)
};

// --- Custom Components ---

const StatCard = ({ title, value, unit, icon: Icon, colorClass }) => (
    <div className={`p-6 rounded-xl shadow-lg bg-white border-b-4 ${colorClass}`}>
        <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</h3>
            {/* Render the Icon component using JSX syntax */}
            <Icon className={`w-6 h-6 ${colorClass.replace('border-', 'text-')}`} />
        </div>
        <div className="mt-2 flex items-baseline">
            <p className="text-4xl font-extrabold text-gray-900">
                {value.toFixed(2)}
            </p>
            <p className="ml-2 text-md font-medium text-gray-500">{unit}</p>
        </div>
    </div>
);

const NetBalanceIndicator = ({ balance }) => {
    let status, color;
    let IconComponent; // Use a consistently named variable for the component

    if (balance > 100) {
        status = 'Carbon Positive';
        color = 'bg-green-100 text-green-700 border-green-500';
        IconComponent = DollarSign;
    } else if (balance > 0) {
        status = 'Slightly Positive';
        color = 'bg-lime-100 text-lime-700 border-lime-500';
        IconComponent = DollarSign;
    }
    else if (balance >= -100) {
        status = 'Near Neutral';
        color = 'bg-yellow-100 text-yellow-700 border-yellow-500';
        IconComponent = Zap;
    } else {
        status = 'Carbon Negative';
        color = 'bg-red-100 text-red-700 border-red-500';
        IconComponent = BarChart2;
    }

    return (
        <div className={`p-6 rounded-xl shadow-lg border-2 ${color}`}>
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold uppercase tracking-wider">Net Carbon Balance</h3>
                {/* Render the Icon component using JSX syntax */}
                <IconComponent className="w-8 h-8" /> 
            </div>
            <div className="mt-4 flex flex-col">
                <p className="text-5xl font-extrabold">
                    {balance.toFixed(2)}
                </p>
                <p className="text-xl font-medium mt-2">{status}</p>
            </div>
        </div>
    );
};

// --- Main Application Component ---

const App = () => {
    const [db, setDb] = useState(null);
    const [auth, setAuth] = useState(null);
    const [userId, setUserId] = useState(null);
    const [isAuthReady, setIsAuthReady] = useState(false);
    
    // Real-time Data State
    const [data, setData] = useState({
        emissions: 0,
        sequestration: 0,
        config: initialConfig,
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // 1. Firebase Initialization and Authentication
    useEffect(() => {
        try {
            const app = initializeApp(firebaseConfig);
            const firestore = getFirestore(app);
            const authService = getAuth(app);
            
            setDb(firestore);
            setAuth(authService);

            // Sign in handler
            const signIn = async () => {
                try {
                    if (initialAuthToken) {
                        const userCredential = await signInWithCustomToken(authService, initialAuthToken);
                        setUserId(userCredential.user.uid);
                    } else {
                        const userCredential = await signInAnonymously(authService);
                        setUserId(userCredential.user.uid);
                    }
                } catch (err) {
                    console.error("Firebase authentication error:", err);
                    setError("Failed to authenticate with Firebase.");
                    setUserId(crypto.randomUUID()); // Fallback non-auth user ID
                } finally {
                    setIsAuthReady(true);
                }
            };
            signIn();

        } catch (e) {
            console.error("Firebase initialization failed:", e);
            setError("Failed to initialize Firebase services.");
            setIsAuthReady(true); // Still mark as ready to prevent infinite loading
        }
    }, []);

    // Memoized Net Balance Calculation
    const netBalance = useMemo(() => {
        return data.sequestration - data.emissions;
    }, [data.emissions, data.sequestration]);

    // Calculate simulated results based on current config
    const calculateResults = useCallback((config) => {
        const emissions = config.numVehicles * config.co2PerVehicleFactor;
        const sequestration = config.forestAreaAcres * config.sequestrationPerAcreRate;
        return { emissions, sequestration };
    }, []);

    // 2. Real-Time Data Listener (onSnapshot)
    useEffect(() => {
        if (!isAuthReady || !db) return;

        const dataRef = doc(db, SIMULATION_DOC_PATH);

        // Function to initialize the document if it doesn't exist
        const initializeDoc = async () => {
            const docSnap = await getDoc(dataRef);
            if (!docSnap.exists()) {
                const initial = calculateResults(initialConfig);
                await setDoc(dataRef, { ...initial, config: initialConfig });
                console.log("Initialized new real-time document.");
            }
        };
        
        initializeDoc();

        const unsubscribe = onSnapshot(dataRef, (docSnapshot) => {
            if (docSnapshot.exists()) {
                const liveData = docSnapshot.data();
                setData(liveData);
                setIsLoading(false);
                setError(null);
            } else {
                // Should not happen after initialization check, but handling it.
                setData({ emissions: 0, sequestration: 0, config: initialConfig });
                setIsLoading(false);
            }
        }, (err) => {
            console.error("Firestore real-time error:", err);
            setError("Lost connection to real-time data.");
            setIsLoading(false);
        });

        return () => unsubscribe();
    }, [isAuthReady, db, calculateResults]);

    // 3. Update Function (Triggers real-time change for all users)
    const updateConfigAndRecalculate = useCallback(async (newConfig) => {
        if (!db) return;
        setIsLoading(true);
        setError(null);
        
        const { emissions, sequestration } = calculateResults(newConfig);
        const dataRef = doc(db, SIMULATION_DOC_PATH);

        try {
            // Update the document with new calculated results and config
            await setDoc(dataRef, {
                emissions: parseFloat(emissions.toFixed(2)),
                sequestration: parseFloat(sequestration.toFixed(2)),
                config: newConfig,
            });
            // The onSnapshot listener will update the local state (setData)
        } catch (e) {
            console.error("Error writing to Firestore:", e);
            setError("Failed to push changes. Check network connection.");
        } finally {
            setIsLoading(false);
        }
    }, [db, calculateResults]);


    const handleInputChange = (key, value) => {
        const numericValue = parseFloat(value);
        if (isNaN(numericValue) || numericValue < 0) return; // Basic validation

        const newConfig = {
            ...data.config,
            [key]: numericValue,
        };
        
        // Immediately update Firestore
        updateConfigAndRecalculate(newConfig);
    };

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-red-50 text-red-700 p-8">
                <p className="font-semibold">{error}</p>
            </div>
        );
    }
    
    if (isLoading && isAuthReady) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
                <p className="ml-4 text-lg text-gray-600">Loading Real-Time Data...</p>
            </div>
        );
    }

    const { config } = data;

    return (
        <div className="min-h-screen bg-gray-50 p-4 md:p-8 font-sans">
            {/* REMOVED: <script src="https://cdn.tailwindcss.com"></script> and <style jsx> block */}
            <header className="mb-8 text-center">
                <h1 className="text-4xl font-extrabold text-gray-900 flex items-center justify-center">
                    <Zap className="w-8 h-8 mr-3 text-blue-600" />
                    Real-Time Carbon Balance Tracker
                </h1>
                <p className="mt-2 text-lg text-gray-600">Monitoring Ecosystem Health: Emissions vs. Sequestration</p>
                <p className="mt-1 text-sm text-gray-500">
                    <span className="font-mono bg-gray-200 px-2 py-0.5 rounded">User ID: {userId || 'Authenticating...'}</span>
                </p>
            </header>
            
            <div className="max-w-7xl mx-auto">
                {/* Real-Time Metrics Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-10">
                    <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Emissions Card */}
                        <StatCard 
                            title="Total CO2 Emissions" 
                            value={data.emissions} 
                            unit="tons CO2/year" 
                            icon={Truck} 
                            colorClass="border-red-500"
                        />
                        {/* Sequestration Card */}
                        <StatCard 
                            title="Forest CO2 Sequestration" 
                            value={data.sequestration} 
                            unit="tons CO2/year" 
                            icon={TreePine} 
                            colorClass="border-green-500"
                        />
                    </div>
                    {/* Net Balance Indicator (Spans 1 column on desktop) */}
                    <NetBalanceIndicator balance={netBalance} />
                </div>
                
                {/* Simulation Control Panel and Diagram */}
                <div className="bg-white p-8 rounded-xl shadow-2xl">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-3">Simulation Controls (Real-Time Input)</h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Input Group 1: Emissions */}
                        <div>
                            <h3 className="text-xl font-semibold text-red-600 mb-4 flex items-center">
                                <Truck className="w-5 h-5 mr-2" /> Vehicular Impact
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="numVehicles" className="block text-sm font-medium text-gray-700">
                                        Number of Vehicles on Road (Units)
                                    </label>
                                    <input
                                        id="numVehicles"
                                        type="number"
                                        min="0"
                                        step="100"
                                        value={config.numVehicles}
                                        onChange={(e) => handleInputChange('numVehicles', e.target.value)}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 text-lg focus:border-red-500 focus:ring-red-500 transition duration-150"
                                        aria-label="Number of vehicles"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="emissionFactor" className="block text-sm font-medium text-gray-700">
                                        CO2 Emission Factor (tons/vehicle/year)
                                    </label>
                                    <input
                                        id="emissionFactor"
                                        type="number"
                                        min="0.1"
                                        step="0.1"
                                        value={config.co2PerVehicleFactor}
                                        onChange={(e) => handleInputChange('co2PerVehicleFactor', e.target.value)}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 text-lg focus:border-red-500 focus:ring-red-500 transition duration-150"
                                        aria-label="Emission factor"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Input Group 2: Sequestration */}
                        <div>
                            <h3 className="text-xl font-semibold text-green-600 mb-4 flex items-center">
                                <TreePine className="w-5 h-5 mr-2" /> Forest Sequestration
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="forestArea" className="block text-sm font-medium text-gray-700">
                                        Forest Area for Sequestration (Acres)
                                    </label>
                                    <input
                                        id="forestArea"
                                        type="number"
                                        min="0"
                                        step="100"
                                        value={config.forestAreaAcres}
                                        onChange={(e) => handleInputChange('forestAreaAcres', e.target.value)}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 text-lg focus:border-green-500 focus:ring-green-500 transition duration-150"
                                        aria-label="Forest area"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="sequestrationRate" className="block text-sm font-medium text-gray-700">
                                        Sequestration Rate (tons/acre/year)
                                    </label>
                                    <input
                                        id="sequestrationRate"
                                        type="number"
                                        min="0.1"
                                        step="0.1"
                                        value={config.sequestrationPerAcreRate}
                                        onChange={(e) => handleInputChange('sequestrationPerAcreRate', e.target.value)}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 text-lg focus:border-green-500 focus:ring-green-500 transition duration-150"
                                        aria-label="Sequestration rate"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <p className="text-sm text-gray-500">
                            *This application uses simplified, static factors for real-time simulation (e.g., all vehicles are assumed to be the same).
                            Any change you make here is instantly reflected across all connected sessions.
                        </p>
                    </div>
                </div>
                
                {/* Diagram Section */}
                <div className="mt-10 bg-white p-8 rounded-xl shadow-2xl">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">The Carbon Cycle Context</h2>
                    <p className="text-gray-600 mb-4">The core concept of this tracker is balancing human-induced atmospheric carbon (emissions) against the natural capacity of ecosystems to absorb it (sequestration). </p>
                    <p className="text-gray-600 mt-4">Maintaining a balance, or ideally achieving a "Carbon Positive" state, requires both reducing inputs (Vehicular Emissions) and maximizing outputs (Forest Sequestration).</p>
                </div>
            </div>
        </div>
    );
};

export default App;