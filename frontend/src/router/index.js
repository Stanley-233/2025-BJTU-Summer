import { createRouter, createWebHistory } from 'vue-router';
import WelcomePage from '../views/WelcomePage.vue';
import DangerRecognition from '../views/DangerRecognition.vue';
import CityVisualization from '../views/CityVisualization.vue';
import DataAnalysisPage from '../views/DataAnalysisPage.vue';
import ConsolePage from '../views/ConsolePage.vue';
import LoginSelectionPage from '../views/LoginSelectionPage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import FaceRecognition from '../views/FaceRecognition.vue';
import EmailLoginPage from '../views/EmailLoginPage.vue';
import NotFound from '../views/NotFound.vue';
import PopulationVisualize from '../views/PopulationVisualize.vue';
import AnalyticalGraph from '@/views/AnalyticalGraph.vue';
const routes = [
  { path: '/', name: 'WelcomePage', component: WelcomePage },
  { path: '/danger', name: 'DangerRecognition', component: DangerRecognition },
  { path: '/city', name: 'CityVisualization', component: CityVisualization },
  { path: '/data-analysis', name: 'DataAnalysisPage', component: DataAnalysisPage },
  { path: '/console', name: 'ConsolePage', component: ConsolePage },
  { path: '/login_select', name: 'LoginSelectionPage', component: LoginSelectionPage },
  { path: '/login', name: 'LoginPage', component: LoginPage },
  { path: '/register', name: 'RegisterPage', component: RegisterPage },
  { path: '/face', name: 'FaceRecognition', component: FaceRecognition },
  { path: '/email_login', name: 'EmailLoginPage', component: EmailLoginPage },
  { path: '/population-visualize', name: 'PopulationVisualize', component: PopulationVisualize },
  {
    path: '/analytical-graph', // 新路由
    name: 'AnalyticalGraph',
    component: AnalyticalGraph
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
