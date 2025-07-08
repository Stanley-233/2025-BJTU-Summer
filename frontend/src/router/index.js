import { createRouter, createWebHistory } from 'vue-router';
import WelcomePage from '../views/WelcomePage.vue';
import DangerRecognition from '../views/DangerRecognition.vue';
import CityVisualization from '../views/CityVisualization.vue';
import ConsolePage from '../views/ConsolePage.vue';
import LoginSelectionPage from '../views/LoginSelectionPage.vue';

const routes = [
  { path: '/', name: 'WelcomePage', component: WelcomePage },
  { path: '/danger', name: 'DangerRecognition', component: DangerRecognition },
  { path: '/city', name: 'CityVisualization', component: CityVisualization },
  { path: '/console', name: 'ConsolePage', component: ConsolePage },
  { path: '/login_select', name: 'LoginSelectionPage', component: LoginSelectionPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
