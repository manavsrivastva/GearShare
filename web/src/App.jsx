
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import Home from "./pages/Home";
import ItemDetails from "./pages/ItemDetails";
import MyRentals from "./pages/MyRentals";
import Basket from "./pages/Basket";
import AddItem from "./pages/AddItem";

import { CustomerProvider } from "./context/CustomerContext";
import { BasketProvider } from "./context/BasketContext";

function App() {
  return (
    <CustomerProvider>
      <BasketProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/gear/:sku" element={<ItemDetails />} />
              <Route path="/me" element={<MyRentals />} />
              <Route path="/basket" element={<Basket />} />
              <Route path="/admin/add" element={<AddItem />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </BasketProvider>
    </CustomerProvider>
  );
}

export default App;
