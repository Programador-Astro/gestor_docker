import React, { useState } from 'react';

import { Link } from 'react-router-dom';
import { loginUser } from './engine.js';
import { Main } from './styles.js';
import Navbar from '../components/nav_bar.jsx';
import {
  Container,
  Title,
  Input,
  Button,
  ErrorMessage
} from './styles.js';

function Veiculos() {

  return (
    <Container>
      <Navbar />
      <Main> <button><Link to="/logistica/checklist">Checklist</Link></button> <button><Link to="/logistica/novo_veiculo">Cadastrar Veiculo</Link></button> </Main>
    </Container>
  );
}

export default Veiculos;
