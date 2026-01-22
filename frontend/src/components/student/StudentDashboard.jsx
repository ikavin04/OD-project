import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Plus, 
  Calendar, 
  MapPin, 
  Upload,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import toast from 'react-hot-toast';
import api from '../../utils/api';

// Coimbatore institutions list - replaced with Tamil Nadu colleges list
const TAMILNADU_COLLEGES = [
  'Ponjesly College of Engineering, Agesteeswaram',
  'SACS M.A.V.M.M. Engineering College, AlagarKoil',
  'M.N.S.K. College of Engineering, Alangudy Taluk',
  'SCAD College of Engineering, Ambasamudram',
  'Udaya School of Engineering, Ammandivilai Post',
  'B.K.R. College of Engineering and Technology, Arakkonam',
  'Jeyamatha Engineering College, Aralvaimozhi',
  'V.S.B. Engineering College, Aravakkurichi Taluk',
  'Anna University Tiruchirappali, Ariyalur',
  'Sri Balaji Chockalingam Engineering College, Arni Taluk',
  'Sree Sowdambika College of Engineering, Aruppukottai Taluk',
  'Bharathiyar Institute of Engineering for Women, Attur Taluk',
  'Greentech College of Engineering for Women, Attur Taluk',
  'Tagore Institute of Engineering and Technology, Attur Taluk',
  'Maharaja Prithvi Engineering College, Avinashi',
  'Maharaja Engineering College, Avinashi Taluk',
  'J.P. College of Engineering, Ayikudy Tenkasi Taluk',
  'Annai Vailankanni College of Engineering, Azhagapapuram (PO)',
  'Govt. College of Engineering, Bargur',
  'Asan Memorial College of Engineering and Technology, Chengalpattu',
  'Anand Institute of Higher Technology, Chengalpattu Taluk',
  'Indira Gandhi College of Engineering and Technology for Women, Chengalpattu Taluk',
  'S.R.R. Engineering College, Chengalpattu Taluk',
  'SRM University (S.R.M. Engineering College), Chengalpattu Taluk',
  'Valliammai Engineering College, Chengalpattu Taluk',
  'A.R.M. College of Engineering and Technology, Chengalpet',
  'Prince Shri Venkateshwara Padmavathy Engineering College, Chengalpet Taluk',
  'Mohamed Sathak A.J. College of Engineering, Chengelpet Taluk',
  'S.M.K. Fomra Institute of Technology, Chengelput Taluk',
  'A.C. College of Technology, Chennai',
  'Aalim Muhammed Salegh College of Engineering, Chennai',
  'Alpha College of Engineering, Chennai',
  'B.S. Abdur Rahman University (B.S. Abdur Rahman Crescent Engineering College), Chennai',
  'Bharath University (Bharath Institute of Higher Education and Research), Chennai',
  'Central Institute of Plastic Engineering and Technology (CIPET), Chennai',
  'Chennai College of Engineering and Technology, Chennai',
  'Dhaanish Ahmed College of Engineering, Chennai',
  'Dhanalakshmi College of Engineering, Chennai',
  'Dr. MGR University (Dr. M.G.R. Educational and Research Insitute), Chennai',
  'Easwari Engineering College, Chennai',
  'G.K.M. College of Engineering and Technology, Chennai',
  'Gojan School of Business and Technology, Chennai',
  'Gopal Ramalingam Memorial Engineering College, Chennai',
  'Hindustan University (Hindustan College of Engineering), Chennai',
  'J.A. Institute of Engineering and Technology, Chennai',
  'Jeppiaar Engineering College, Chennai',
  'Jerusalem College of Engineering, Chennai',
  'K.C.G. College of Technology, Chennai',
  'Madha Engineering College, Chennai',
  'Madras Institute of Technology, Chennai',
  'Measi Academy of Architecture, Chennai',
  'Meenakshi College of Engineering, Chennai',
  'Meenakshi Sundararajan Engineering College, Chennai',
  'Misrimal Navajee Munoth Jain Engineering College, Chennai',
  'New Prince Shri Bhavani College of Engineering and Technology, Chennai',
  'P.M.R. Engineering College, Chennai',
  'P.M.R. Institute of Technology, Chennai',
  'Panimalar Engineering College, Chennai',
  'Panimalar Institute of Technology, Chennai',
  'Raja Rajeswari Engineering College, Chennai',
  'Sakthi Engineering College, Chennai',
  'Sathyabama University (Sathyabama Engineering College), Chennai',
  'Sree Sastha Institute of Engineering and Technology, Chennai',
  'Sri Lakshmi Ammal Engineering College, Chennai',
  'Sri Muthukumaran Institute of Technology, Chennai',
  'Sri Ramanujar Engineering College, Chennai',
  'Sri Sai Ram Institute of Technology, Chennai',
  'Sri Sairam Engineering College, Chennai',
  'Sri Sivasubramaniya Nadar College of Engineering, Chennai',
  'Srinivasa Institute of Engineering and Technology, Chennai',
  'St. Peter\'s University (St. Peters Engineering College), Chennai',
  'T.J. Institute of Technology, Chennai',
  'Tagore Engineering College, Chennai',
  'Thangavelu Engineering College, Chennai',
  'Vel Tech Dr.RR and Dr.SR Technical University (Vel Tech Engineering College), Chennai',
  'Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College, Chennai',
  'Vel Tech Multi Tech Dr.Rangarajan Dr.Sakunthala Engineering College, Chennai',
  'Velammal Engineering College, Chennai',
  'Vel\'s Srinivasa College of Engineering and Technology, Chennai',
  'College of Engineering, Guindy, Chennai',
  'Adhiparasakthi Engineering College, Cheyyar Taluk',
  'Arulmigu Meenakshi Amman College of Engineering, Cheyyar Taluk',
  'Annamalai University, Chidambaram',
  'St. Xavier Catholic College of Engineering, Chunkankadai',
  'Adithya Institute of Technology, Coimbatore',
  'Agricultural Engineering College and Research Institute, Coimbatore',
  'Amrita Vishwa Vidyapeetham University (Amrita School of Engineering), Coimbatore',
  'Avinashilingam University for Women (Avinashilingam Institute for Home Science and Higher Education for Women), Coimbatore',
  'Coimbatore Institute of Engineering and Information Technology, Coimbatore',
  'Coimbatore Institute of Technology, Coimbatore',
  'Dr. N.G.P. Institute of Technology, Coimbatore',
  'EASA College of Engineering and Technology, Coimbatore',
  'Govt. College of Technology, Coimbatore',
  'Hindustan Institute of Technology, Coimbatore',
  'Hindusthan College of Engineering and Technology, Coimbatore',
  'Hindusthan Institute of Technology, Coimbatore',
  'Indus College of Engineering, Coimbatore',
  'Jawaharlal Institute of Technology, Coimbatore',
  'K.G.I.S.L. Institute of Technology, Coimbatore',
  'K.T.V.R. Knowledge Park for Engineering and Technology, Coimbatore',
  'Kalaignar Karunanidhi Institute of Technology, Coimbatore',
  'Karpagam College of Engineering, Coimbatore',
  'Karpagam Institute of Technology, Coimbatore',
  'Karunya University (Karunya Institute of Technology), Coimbatore',
  'Kathir College of Engineering, Coimbatore',
  'Kumaraguru College of Technology, Coimbatore',
  'Maharaja Institute of Technology, Coimbatore',
  'Nehru Institute of Engineering and Technology, Coimbatore',
  'Nyruthi Institute of Technology and Science, Coimbatore',
  'P.P.G. Institute of Technology, Coimbatore',
  'P.S.G. College of Technology, Coimbatore',
  'Ranganathan Engineering College, Coimbatore',
  'S.N.S. College of Engineering, Coimbatore',
  'S.N.S. College of Technology, Coimbatore',
  'S.S.K. College of Engineering and Technology, Coimbatore',
  'Sri Krishna College of Engineering and Technology, Coimbatore',
  'Sri Ramakrishna Institute of Technology, Coimbatore',
  'Sri Shakthi Institute of Engineering and Technology, Coimbatore',
  'Tamilnadu School of Architecture, Coimbatore',
  'V.L.B. Janaki Ammal College of Engineering and Technology, Coimbatore',
  'Sri Ramakrishna Engineering College, Coimbatore NorthTaluk',
  'C.S.I. College of Engineering, Coonoor Taluk',
  'Dr. Navalar Nedunchezhiyan College of Engineering, Cuddalore',
  'Sri Jayaram Engineering College, Cuddalore',
  'Krishnasamy College of Engineering and Technology, Cuddalore Taluk',
  'Varuvan Vadivelan Institute of Technology, Dharmapuri',
  'P.S.N.A. College of Engineering and Technology, Dindigul',
  'R.V.S. College of Engineering and Technology, Dindugul',
  'Vickram College of Engineering, Enathi',
  'Sun College of Engineering and Technology, Erachakulam Post',
  'C.M.S. College of Engineering, Ernapuram Post',
  'Bannari Amman Institute of Technology, Erode',
  'Erode Sengunthar Engineering College, Erode',
  'Institute of Road and Transport Technology, Erode',
  'Kongu Engineering College, Erode',
  'Nandha Engineering College, Erode',
  'Nandha Institute of Technology, Erode',
  'Surya Engineering College, Erode',
  'Velalar College of Engineering and Technology, Erode',
  'Kings College of Engineering, Gandarvakottai Taluk',
  'J.K.K. Muniraja Institute of Technology, Gobi Taluk',
  'Shree Venkateshwara Hi-Tech Engineering College, Gobichettipalayam',
  'R.M.D. Engineering College, Gummidipoondi Taluk',
  'R.M.K. College of Engineering and Technology, Gummidipoondi Taluk',
  'R.M.K. Engineering College, Gummidipoondi Taluk',
  'Er. Perumal Manimekalai College of Engineering, Hosur',
  'Adhiyamaan College of Engineering, Hosur Taluk',
  'St. Michael College of Engineering and Technology, Kalayarkoil',
  'Vins Christian College of Engineering, Kalkulam Taluk',
  'Maha Bharathi Engineering College, Kallakurichi Taluk',
  'Adhi College of Engineering and Technology, Kancheepuram',
  'D.M.I. College of Engineering, Kancheepuram',
  'JEI Mathaajee College of Engineering, Kancheepuram',
  'Kanchi Pallavan Engineering College, Kancheepuram',
  'P.T. Lee Chengalvaraya Naicker College of Engineering and Technology, Kancheepuram',
  'SCSVMV University (Sri Chandrasekharendra Saraswathi Viswa Mahavidyalaya), Kancheepuram',
  'Pallavan College of Engineering, Kancheepuram Taluk',
  'Aarupadai Veedu Institute of Technology, Kanchipuram',
  'St. Joseph\'s College of Engineering, Kanchipuram',
  'Lord Venkateshwara Engineering College, Kanchipuram Taluk',
  'C.S.I. Institute of Technology, Kanyakumari',
  'James College of Engineering and Technology, Kanyakumari',
  'K.N.S.K. College of Engineering, Kanyakumari',
  'Narayanaguru College of Engineering, Kanyakumari',
  'A.C. College of Engineering and Technology, Karaikudi',
  'Central Electro Chemical Research Institute, Karaikudi',
  'Sethu Institute of Technology, Kariapatti',
  'Tejaa Shakthi Institute of Technology for Women, Karumathampatti',
  'Tamil Nadu College of Engineering, Karumathampatti Post',
  'Bethlahem Institute of Engineering, Karungal',
  'Chettinad College of Engineering and Technology, Karur',
  'M. Kumarasamy College of Engineering, Karur Taluk',
  'Kingston Engineering College, Katpadi Taluk',
  'Mohamed Sathak Engineering College, Kilakarai',
  'Sri Eshwar College of Engineering, Kinathukadavu',
  'Kodaikanal Institute of Technology, Kodaikanal',
  'Sudharsan Engineering College, Kolathur Taluk',
  'Excel College of Engineering for Women, Komarapalayam',
  'Excel Engineering College, Komarapalayam',
  'S.S.M. College of Engineering, Komarapalayam',
  'Trichy Engineering College, Konalai',
  'Info Institute of Engineering, Kovilpalayam',
  'National Engineering College, Kovilpatti',
  'P.S.V. College of Engineering and Technology, Krishnagiri',
  'Thirumalai Engineering College, Krishnapuram Post',
  'Mookambigai College of Engineering, Kulathur Taluk',
  'Lord Jegannath College of Engineering and Technology, Kumarapuramthoppur Post',
  'Arasu Engineering College, Kumbakonam',
  'Shri Angala Amman College of Engineering and Technology, Lalgudi Taluk',
  'K.L.N. College of Engineering, Madurai',
  'K.L.N. College of Information Technology, Madurai',
  'Latha Mathavan Engineering College, Madurai',
  'P.T.R. College of Engineering and Technology, Madurai',
  'Raja College of Engineering and Technology, Madurai',
  'Thiagarajar College of Engineering, Madurai',
  'Velammal College of Engineering and Technology, Madurai',
  'Shri Andal Alagar College of Engineering, Madurantakam Taluk',
  'A.C.T. College of Engineering and Technology, Maduranthagam',
  'Karpaga Vinayaga College of Engineering and Technology, Maduranthagam Taluk',
  'Dhanalakshmi Srinivasan College of Engineering and Technology, Mamallapuram',
  'K. Ramakrishnan College of Engineering, Manachanallur Taluk',
  'Kurinji College of Engineering and Technology, Manapparai',
  'M.A.M. College of Engineering, Mannachanallur Taluk',
  'A.R.J. College of Engineering and Technology, Mannargudi',
  'Paventhar Bharathidasan College of Engineering and Technology, Mathur',
  'A.V.C. College of Engineering, Mayiladutarai',
  'The Kavery Engineering College, Mettur',
  'Annai Mathammal Sheela Engineering College, Namakkal',
  'Gnanamani College of Technology, Namakkal',
  'P.G.P. College of Engineering and Technology, Namakkal',
  'Selvam College of Technology, Namakkal',
  'National College of Engineering, Nanguneri Taluk',
  'N.P.R. College of Engineering and Technology, Natham',
  'Immanuvel Arasar J.J. College of Engineering, Nattalam',
  'Jeyaraj Annapackiam CSI College of Engineering, Nazareth',
  'Christian College of Engineering and Technology, Oddanchatram',
  'Narasu\'s Sarathy Institute of Technology, Omalur Taluk',
  'Paavai College of Engineering, Pachal',
  'Paavai Engineering College, Pachal',
  'Sapthagiri College of Engineering, Palacode Taluk',
  'Sri Subramaniya College of Engineering and Technology, Palani',
  'Francis Xavier Engineering College, Palayamkottai',
  'P.S.N. Engineering College, Palayamkottai',
  'P.S.N. College of Engineering and Technology, Palayamkottai Taluk',
  'Park College of Engineering Technology, Palladam Taluk',
  'Ganapathy Chettiar College of Engineering and Technology, Paramakudi',
  'Jayam College of Engineering and Technology, Pennagaram Taluk',
  'Dhanalakshmi Srinivasan Engineering College, Perambalur',
  'Rover Engineering College, Perambalur',
  'Srinivasan Engineering College, Perambalur',
  'Odaiyappa College of Engineering and Technology, Periyakulam Taluk',
  'Maharaja Engineering College for Women, Perundurai',
  'Sasurie College of Engineering, Perundurai',
  'M.P.Nachimuthu M.Jaganathan Engineering College, Perundurai Taluk',
  'Cauvery College of Engineering and Technology, Perur',
  'Dr. Mahalingam College of Engineering and Technology, Pollachi',
  'P.A. College of Engineering and Technology, Pollachi',
  'Velammal Institute of Technology, Ponneri Taluk',
  'M.A.R. College of Engineering and Technology, Pudukkottai',
  'Cape Institute of Technology, Radhapuram Taluk',
  'Syed Ammal Engineering College, Ramanathapuram',
  'Muthayammal Engineering College, Rasipuram',
  'A.V.S. Engineering College, Salem',
  'Govt. College of Engineering, Salem',
  'Sona College of Technology, Salem',
  'Vinayaka Mission\'s Kirupanada Variyar Engineering College, Salem',
  'Rabidhranath Tagore College of Engineering for Women, Sankari Taluk',
  'M.A.M. College of Engineering and Technology, Siruganur',
  'Seethai Ammal Engineering College, Sivagangai',
  'Pandiyan Saraswathi Yadav Engineering College, Sivagangai Taluk',
  'Mahakavi Bharathiyar College of Engineering and Technology, Sivagiri Taluk',
  'S. Veerasamy Chettiar College of Engineering and Technology, Sivagiri Taluk',
  'MEPCO Schlenk Engineering College, Sivakasi',
  'P.S.R. Engineering College, Sivakasi',
  'P.S.R. Rengasamy College of Engineering for Women, Sivakasi',
  'Kalsar College of Engineering, Sriperambudur Taluk',
  'Sakthi Mariamman Engineering College, Sriperumbudhur',
  'Apollo Engineering College, Sriperumbudur',
  'Kings Engineering College, Sriperumbudur',
  'P.B. College of Engineering, Sriperumbudur',
  'Rajiv Gandhi College of Engineering, Sriperumbudur',
  'Rrase College of Engineering, Sriperumbudur',
  'Sri Venkateswara College of Engineering, Sriperumbudur',
  'V.K.K. Vijayan Engineering College, Sriperumbudur',
  'Loyola Institute of Technology, Sriperumbudur Taluk',
  'Rajalakshmi Engineering College, Sriperumbudur Taluk',
  'Rajalakshmi Institute of Technology, Sriperumbudur Taluk',
  'Saveetha Engineering College, Sriperumbudur Taluk',
  'Maamallan Institute of Technology, Sriperumpudur',
  'St. Joseph College of Engineering, Sriperumpudur',
  'Arignar Anna Institute of Science and Technology, Sriperumpudur Taluk',
  'Sri Krishna Engineering College, Sriperumpudur Taluk',
  'J.J. College of Engineering and Technology, Srirangam',
  'Saranathan College of Engineering, Srirangam Taluk',
  'Kalasalingam Institute of Technology, Srivilliputhur',
  'V.P.M.M. Engineering College for Women, Srivilliputtur Taluk',
  'R.V.S. College of Engineering and Technology, Sulur',
  'Parisutham Institute of Technology and Science, Thanjavur',
  'PRIST University (P.R. Engineering College), Thanjavur',
  'PRIST University (Ponnaiyah Ramajayam College of Engineering and Technology), Thanjavur',
  'SASTRA University (Shanmugha Arts Science Technology and Research Academy), Thanjavur',
  'St. Joseph\'s College of Engineering and Technology, Thanjavur',
  'Bharath Niketan Engineering College, Theni',
  'Theni Kammavar Sangam College of Technology, Theni',
  'K.S. Rangasamy College of Technology, Thiruchengode Taluk',
  'K.S.R. College of Engineering, Thiruchengode Taluk',
  'The New Royal College of Engineering and Technology, Thirukkalukundram Taluk',
  'Mount Zion College of Engineering, Thirumayam Taluk',
  'Shanmuganathan Engineering College, Thirumayam Taluk',
  'Balaji Institute of Engineering and Technology, Thiruporur',
  'Sri Venkateswara Institute of Science and Technology, Thiruppachur Post',
  'Lakshmi Chand Rajani College of Engineering and Technology, Thiruthani',
  'Indira Institute of Engineering and Technology, Thiruvallur',
  'S.K.R. Engineering College, Thiruvallur',
  'Sri Venkateswara College of Engineering and Technology, Thiruvallur',
  'Prathyusha Institute of Technology and Management, Thiruvallur Taluk',
  'Anjalai Ammal Mahalingam Engineering College, Thiruvarur',
  'S.A. Engineering College, Thiruverkadu Post',
  'Dr. G.U. Pope College of Engineering, Thoothukudi',
  'Jayalakshmi Institute of Technology, Thoppur',
  'Loyola Institute of Technology and Science, Thovalai',
  'Noorul Islam University (Noorul Islam College of Engineering), Thuckalay',
  'Jayaram College of Engineering and Technology, Thuraiyur Taluk',
  'University College of Engineering, Tindivanam',
  'Mailam Engineering College, Tindivanam Taluk',
  'J.K.K. Nataraja College of Engineering and Technology, Tiruchengode',
  'Mahendra Engineering College for Women, Tiruchengode',
  'Mahendra Institute of Technology, Tiruchengode',
  'Sengunthar College of Engineering for Women, Tiruchengode',
  'Sengunthar Engineering College, Tiruchengode',
  'Vidhya Vikkas College of Engineering and Technology, Tiruchengode',
  'Vivekanadha Institute of Engineering and Technology for Women, Tiruchengode',
  'Vivekanadha College of Engineering for Women, Tiruchengode Talu',
  'Mahendra Engineering College, Tiruchengode Taluk',
  'Govt. College of Engineering, Tirunelveli',
  'Joe Suresh Engineering College, Tirunelveli',
  'Sardar Raja College of Engineering, Tirunelveli',
  'Einstein College of Engineering, Tirunelveli Taluk',
  'Sri Nandhanam College and Technology, Tirupattur',
  'Bharathidasan Engineering College, Tirupattur Taluk',
  'Angel College of Engineering and Technology, Tiruppur',
  'Jaya Engineering College, Tiruvallur',
  'Magna College of Engineering, Tiruvallur',
  'Bhajarang Engineering College, Tiruvallur Taluk',
  'Sri Ram Engineering College, Tiruvallur Taluk',
  'Arunai Engineering College, Tiruvannamalai',
  'S.K.P. Engineering College, Tiruvannamalai',
  'Kamban Engineering College, Tiruvannamalai Taluk',
  'Bharathidasan Institute of Engineering and Technology, Trichy',
  'Indra Ganesan College of Engineering, Trichy',
  'Kongunadu College of Engineering and Technology, Trichy',
  'M.I.E.T. Engineering College, Trichy',
  'National Institute of Technology, Trichy',
  'Oxford Engineering College, Trichy',
  'Anna University Tiruchirappali, Trichy',
  'Dr. Sivanthi Aditanar College of Engineering, Tuticorin',
  'Infant Jesus College of Engineering, Tuticorin',
  'Infant Jesus College of Engineering and Technology, Tuticorin',
  'Annai Teresa College of Engineering, Ulundurpet Taluk',
  'V.R.S. College of Engineering and Technology, Ulundurpet Taluk',
  'SAMS College of Engineering and Technology, Uthokottai Taluk',
  'J.N.N. Institute of Engineering, Uthukottai Taluk',
  'The Rajaas Engineering College, Vadakkangulam',
  'Maha College of Engineering, Valapadi Taluk',
  'Sri Padmavathy College of Engineering, Valarpuram post',
  'Periyar Maniammai University (Periyar Maniammai College of Technology for Women), Vallam',
  'PET Engineering College, Vallioor',
  'Thiruvalluvar College of Engineering and Technology, Vandavasi',
  'Priyadarshini Engineering College, Vaniyambadi',
  'Dr. Paul\'s Engineering College, Vanur Taluk',
  'Sri Aravindar Engineering College, Vanur Taluk',
  'Marthandam College of Engineering and Technology, Veeyanoor',
  'Adhiparasakthi College of Engineering, Vellore',
  'C. Abdul Hakeem College of Engineering and Technology, Vellore',
  'G.G.R. College of Engineering, Vellore',
  'Ganadipathy Tulsi\'s Engineering College, Vellore',
  'Thanthai Periyar Govt. Institute of Technology, Vellore',
  'VIT University (Vellore Institute of Technology), Vellore',
  'Surya College of Engineering and Technology, Vikravandi',
  'A.R. Engineering College, Villupuram',
  'E.S. College of Engineering and Technology, Villupuram',
  'I.F.E.T. College of Engineering, Villupuram',
  'Idhaya Engineering College for Women, Villupuram',
  'University College of Engineering, Villupuram',
  'Kalasalingam University (Arulmigu Kalasalingam College of Engineering), Virudhunagar',
  'Kamaraj College of Engineering and Technology, Virudhunagar',
  'Sri Vidya College of Engineering and Technology, Virudhunagar',
  'Saraswathi Velu College of Engineering, Walajah Taluk',
  'Ranipet Engineering College, Wallajah Taluk'
];

// List of Indian states
const INDIAN_STATES = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry'
];

function StudentDashboard() {
  const { user } = useAuth();
  const [odRequests, setOdRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewRequestForm, setShowNewRequestForm] = useState(false);
  const [pendingProofs, setPendingProofs] = useState([]);
  const [newRequest, setNewRequest] = useState({
    event_name: '',
    from_date: '',
    to_date: '',
    venue: '',
    event_description: '',
    od_type: '',
    host_institution: '',
    location_type: ''
  });
  const [permissionImage, setPermissionImage] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [collegeSearch, setCollegeSearch] = useState('');
  const [showCollegeDropdown, setShowCollegeDropdown] = useState(false);
  const collegeDropdownRef = useRef(null);

  // Filter colleges based on search
  const filteredColleges = collegeSearch
    ? TAMILNADU_COLLEGES.filter(college =>
        college.toLowerCase().includes(collegeSearch.toLowerCase())
      )
    : TAMILNADU_COLLEGES;

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (collegeDropdownRef.current && !collegeDropdownRef.current.contains(event.target)) {
        setShowCollegeDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    fetchODRequests();
    fetchPendingProofs();
  }, []);

  const fetchODRequests = async () => {
    try {
      const response = await api.get('/od-requests');
      setOdRequests(response.data.od_requests || []);
    } catch (error) {
      if (error.response?.status === 401) {
        console.error('Authentication error. User needs to login again.');
        // Clear any invalid tokens
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
        // Redirect to login
        window.location.href = '/login';
      } else {
        console.error('Failed to fetch OD requests:', error);
        toast.error('Failed to load OD requests');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingProofs = async () => {
    try {
      const response = await api.get('/od-requests');
      // Filter for approved requests only
      const approvedRequests = (response.data.od_requests || []).filter(
        req => req.status === 'approved'
      );
      
      // Filter for requests that need proof submission
      const needingProofs = approvedRequests.filter(request => {
        const deadlines = request.deadlines || {};
        const now = new Date();
        
        // Check if attendance proof is overdue
        if (!request.attendance_proof && deadlines.attendance_proof_deadline) {
          const deadline = new Date(deadlines.attendance_proof_deadline);
          if (deadline < now) return true;
        }
        
        // Check if certificate is overdue
        if (request.attendance_proof && !request.certificate && deadlines.certificate_deadline) {
          const deadline = new Date(deadlines.certificate_deadline);
          if (deadline < now) return true;
        }
        
        return false;
      });
      
      setPendingProofs(needingProofs);
    } catch (error) {
      console.error('Failed to fetch pending proofs:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRequest(prev => {
      const updated = {
        ...prev,
        [name]: value
      };
      
      // Auto-fill host institution when intra-college is selected
      if (name === 'od_type' && value === 'intra_college') {
        updated.host_institution = 'KGISL Institute of Technology';
        updated.location_type = ''; // Clear location type for intra-college
        setCollegeSearch(''); // Clear college search
      } else if (name === 'od_type' && value === 'inter_college_within_tn') {
        // Clear host institution for within TN
        updated.host_institution = '';
        updated.location_type = 'Tamil Nadu'; // Auto-set to Tamil Nadu
        setCollegeSearch(''); // Clear college search to show dropdown
      } else if (name === 'od_type' && value === 'inter_college_outside_tn') {
        // Clear host institution when switching to outside TN
        updated.host_institution = '';
        updated.location_type = ''; // Let user choose state
        setCollegeSearch(''); // Clear college search
      } else if (name === 'od_type' && value !== 'inter_college_within_tn' && value !== 'inter_college_outside_tn') {
        // Clear location type if switching away from inter-college
        updated.location_type = '';
      }
      
      return updated;
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please upload only PDF files');
        e.target.value = '';
        return;
      }
      
      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        alert('File size must be less than 5MB');
        e.target.value = '';
        return;
      }
      
      setPermissionImage(file);
    }
  };

  const handleSubmitRequest = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Validate that OD is applied at least 3 days before the event start date
      const today = new Date();
      today.setHours(0, 0, 0, 0); // Reset time to start of day
      const eventStartDate = new Date(newRequest.from_date);
      eventStartDate.setHours(0, 0, 0, 0);
      
      const daysDifference = Math.floor((eventStartDate - today) / (1000 * 60 * 60 * 24));
      
      if (daysDifference < 3) {
        toast.error('OD requests must be submitted at least 3 days before the event start date');
        setSubmitting(false);
        return;
      }

      // Create FormData for file upload
      const formData = new FormData();
      
      // Append all form fields
      Object.keys(newRequest).forEach(key => {
        formData.append(key, newRequest[key]);
      });
      
      // Append permission image as the application file
      if (permissionImage) {
        formData.append('application_file', permissionImage);
      } else {
        throw new Error('OD Permission Letter is required');
      }

      await api.post('/od-requests', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast.success('OD request submitted successfully!');
      setShowNewRequestForm(false);
      setNewRequest({
        event_name: '',
        from_date: '',
        to_date: '',
        venue: '',
        event_description: '',
        od_type: '',
        host_institution: '',
        location_type: ''
      });
      setPermissionImage(null);
      setCollegeSearch(''); // Clear college search
      setShowCollegeDropdown(false); // Close dropdown
      fetchODRequests();
      fetchPendingProofs();
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please refresh the page and try again.');
      } else {
        toast.error(error.response?.data?.error || error.response?.data?.message || 'OD exists already');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-secondary-600';
      case 'approved': return 'text-primary-600';
      case 'rejected': return 'text-secondary-700';
      default: return 'text-secondary-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Student Dashboard</h1>
          <p className="text-secondary-600 mt-1">Welcome, {user?.name}</p>
        </div>
        <button
          onClick={() => setShowNewRequestForm(!showNewRequestForm)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>New OD Request</span>
        </button>
      </div>

      {/* Overdue Proof Notifications */}
      {pendingProofs.length > 0 && (
        <div className="card bg-secondary-100 border-secondary-300">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-6 w-6 text-secondary-700 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-secondary-900 mb-2">Urgent: Overdue Proof Submissions</h3>
              <p className="text-sm text-secondary-800 mb-3">
                You have {pendingProofs.length} OD request{pendingProofs.length > 1 ? 's' : ''} with overdue proof submissions. 
                You cannot apply for new OD requests until these are completed.
              </p>
              <div className="space-y-2">
                {pendingProofs.map((request) => {
                  const deadlines = request.deadlines || {};
                  const now = new Date();
                  let overdueType = '';
                  let daysOverdue = 0;
                  
                  if (!request.attendance_proof && deadlines.attendance_proof_deadline) {
                    const deadline = new Date(deadlines.attendance_proof_deadline);
                    if (deadline < now) {
                      overdueType = 'Attendance Proof';
                      daysOverdue = Math.abs(differenceInDays(now, deadline));
                    }
                  } else if (request.attendance_proof && !request.certificate && deadlines.certificate_deadline) {
                    const deadline = new Date(deadlines.certificate_deadline);
                    if (deadline < now) {
                      overdueType = 'Certificate';
                      daysOverdue = Math.abs(differenceInDays(now, deadline));
                    }
                  }
                  
                  return (
                    <div key={request.id} className="text-sm text-secondary-700 bg-secondary-200 rounded p-2">
                      <strong>{request.event_name}</strong> - {overdueType} overdue by {daysOverdue} day{daysOverdue > 1 ? 's' : ''}
                    </div>
                  );
                })}
              </div>
              <Link
                to="/student/proofs"
                className="inline-flex items-center space-x-1 mt-3 text-sm font-medium text-primary-700 hover:text-primary-900"
              >
                <Upload className="h-4 w-4" />
                <span>Submit Proofs Now</span>
                <ExternalLink className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* New Request Form */}
      {showNewRequestForm && (
        <div className="card">
          <h2 className="text-xl font-semibold text-secondary-900 mb-6">Submit New OD Request</h2>
          
          <form onSubmit={handleSubmitRequest} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="event_name" className="block text-sm font-medium text-secondary-700">
                  Event Name *
                </label>
                <input
                  type="text"
                  id="event_name"
                  name="event_name"
                  required
                  value={newRequest.event_name}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                  placeholder="e.g., Technical Symposium, Conference, etc."
                />
              </div>

              <div>
                <label htmlFor="od_type" className="block text-sm font-medium text-secondary-700">
                  OD Type *
                </label>
                <select
                  id="od_type"
                  name="od_type"
                  required
                  value={newRequest.od_type}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                >
                  <option value="">Select OD Type</option>
                  <option value="intra_college">Intra-College</option>
                  <option value="inter_college_within_tn">Inter College-Within Tamilnadu</option>
                  <option value="inter_college_outside_tn">Inter College-Outside Tamilnadu</option>
                </select>
              </div>

              {newRequest.od_type === 'inter_college_outside_tn' && (
                <div>
                  <label htmlFor="location_type" className="block text-sm font-medium text-secondary-700">
                    State *
                  </label>
                  <select
                    id="location_type"
                    name="location_type"
                    required
                    value={newRequest.location_type}
                    onChange={handleInputChange}
                    className="input-field mt-1"
                  >
                    <option value="">Select State</option>
                    {INDIAN_STATES.map((state, index) => (
                      <option key={index} value={state}>
                        {state}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label htmlFor="host_institution" className="block text-sm font-medium text-secondary-700">
                  Host Institution *
                </label>
                {newRequest.od_type === 'inter_college_within_tn' ? (
                  <div className="relative" ref={collegeDropdownRef}>
                    <input
                      type="text"
                      id="host_institution"
                      name="host_institution"
                      required
                      value={collegeSearch || newRequest.host_institution}
                      onChange={(e) => {
                        setCollegeSearch(e.target.value);
                        setShowCollegeDropdown(true);
                        setNewRequest({ ...newRequest, host_institution: e.target.value });
                      }}
                      onFocus={() => setShowCollegeDropdown(true)}
                      className="input-field mt-1"
                      placeholder="Search or select college..."
                      autoComplete="off"
                    />
                    {showCollegeDropdown && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-secondary-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                        {filteredColleges.length > 0 ? (
                          filteredColleges.map((college, index) => (
                            <div
                              key={index}
                              className="px-4 py-2 hover:bg-primary-50 cursor-pointer text-sm"
                              onClick={() => {
                                setNewRequest({ ...newRequest, host_institution: college });
                                setCollegeSearch(college);
                                setShowCollegeDropdown(false);
                              }}
                            >
                              {college}
                            </div>
                          ))
                        ) : (
                          <div className="px-4 py-2 text-sm text-secondary-500">
                            No colleges found
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <input
                    type="text"
                    id="host_institution"
                    name="host_institution"
                    required
                    value={newRequest.host_institution}
                    onChange={handleInputChange}
                    className="input-field mt-1"
                    placeholder={newRequest.od_type === 'intra_college' ? 'Auto-filled for intra-college' : 'e.g., IIT Madras, Chennai'}
                    readOnly={newRequest.od_type === 'intra_college'}
                  />
                )}
              </div>

              <div>
                <label htmlFor="from_date" className="block text-sm font-medium text-secondary-700">
                  Start Date *
                </label>
                <input
                  type="date"
                  id="from_date"
                  name="from_date"
                  required
                  value={newRequest.from_date}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                />
              </div>

              <div>
                <label htmlFor="to_date" className="block text-sm font-medium text-secondary-700">
                  End Date *
                </label>
                <input
                  type="date"
                  id="to_date"
                  name="to_date"
                  required
                  value={newRequest.to_date}
                  onChange={handleInputChange}
                  className="input-field mt-1"
                />
              </div>
            </div>

            <div>
              <label htmlFor="event_description" className="block text-sm font-medium text-secondary-700">
                Event Description
              </label>
              <textarea
                id="event_description"
                name="event_description"
                rows="3"
                value={newRequest.event_description}
                onChange={handleInputChange}
                className="input-field mt-1"
                placeholder="Additional details about the event..."
              />
            </div>

            <div>
              <label htmlFor="permission_image" className="block text-sm font-medium text-secondary-700">
                OD Permission Letter *
              </label>
              <input
                type="file"
                id="permission_image"
                name="permission_image"
                accept="application/pdf"
                onChange={handleFileChange}
                required
                className="mt-1 block w-full text-sm text-secondary-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-medium
                file:bg-primary-50 file:text-primary-700
                hover:file:bg-primary-100"
              />
              <p className="mt-1 text-xs text-secondary-500">
                Upload permission Letter in PDF format
              </p>
              {permissionImage && (
                <p className="mt-2 text-sm text-primary-600">
                  ✓ Selected: {permissionImage.name}
                </p>
              )}
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={submitting}
                className="btn-primary disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit Request'}
              </button>
              <button
                type="button"
                onClick={() => setShowNewRequestForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* OD Requests List */}
      <div className="card">
        <h2 className="text-xl font-semibold text-secondary-900 mb-6">Your OD Requests</h2>
        
        {odRequests.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <p className="text-secondary-500">No OD requests found</p>
            <p className="text-sm text-secondary-400 mt-1">Submit your first OD request to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {odRequests.map((request) => (
              <div key={request.id} className="border border-secondary-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`flex items-center space-x-2 ${getStatusColor(request.status)}`}>
                      {getStatusIcon(request.status)}
                      <span className="font-medium capitalize">{request.status}</span>
                    </div>
                  </div>
                  <span className="text-sm text-secondary-500">#{request.id}</span>
                </div>

                <h3 className="text-lg font-semibold text-secondary-900 mb-2">{request.event_name}</h3>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-secondary-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span className="text-sm">
                      {format(new Date(request.from_date), 'MMM dd, yyyy')} - {format(new Date(request.to_date), 'MMM dd, yyyy')}
                    </span>
                  </div>
                  <div className="flex items-center text-secondary-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    <span className="text-sm">{request.host_institution || request.venue || 'N/A'}</span>
                    {(request.od_type === 'inter_college_coimbatore' || request.od_type === 'inter_college_others') && request.location_type && (
                      <span className="ml-2 px-2 py-1 text-xs bg-secondary-100 text-secondary-600 rounded-full">
                        {request.location_type === 'within_state' ? 'Within State' : 'Out of State'}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-secondary-600">
                    Submitted: {format(new Date(request.created_at), 'MMM dd, yyyy')}
                  </div>
                </div>

                {request.event_description && (
                  <p className="text-secondary-600 text-sm mb-4">{request.event_description}</p>
                )}

                {/* Proof Submission Section */}
                {request.status === 'pending' && (
                  <div className="mt-4 p-3 bg-primary-50 border border-primary-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Upload className="h-4 w-4 text-primary-600" />
                      <span className="text-sm font-medium text-primary-800">Proof Submission</span>
                    </div>
                    <p className="text-xs text-primary-600 mb-3">
                      After approval, you'll need to submit attendance proof within 3 days and certificate within 1 month.
                    </p>
                    <div className="space-y-2">
                      <div className="text-xs text-secondary-600">
                        <strong>Step 1:</strong> Attendance Proof (event brochure/live photo) - Due 3 days after approval
                      </div>
                      <div className="text-xs text-secondary-600">
                        <strong>Step 2:</strong> Participation Certificate - Due 1 month after attendance proof
                      </div>
                    </div>
                  </div>
                )}

                {request.status === 'approved' && (
                  <div className="mt-4">
                    {(() => {
                      const deadlines = request.deadlines || {};
                      const now = new Date();
                      const hasAttendanceProof = !!request.attendance_proof;
                      const hasCertificate = !!request.certificate;
                      
                      if (hasCertificate) {
                        return (
                          <div className="flex items-center p-3 bg-primary-50 border border-primary-200 rounded-lg">
                            <CheckCircle className="h-5 w-5 text-primary-600 mr-3" />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-primary-800">
                                All proofs submitted
                              </p>
                              <p className="text-xs text-primary-600 mt-1">
                                Attendance proof and certificate completed
                              </p>
                            </div>
                          </div>
                        );
                      } else if (hasAttendanceProof) {
                        const certificateDeadline = deadlines.certificate_deadline ? new Date(deadlines.certificate_deadline) : null;
                        const daysLeft = certificateDeadline ? differenceInDays(certificateDeadline, now) : null;
                        const isOverdue = certificateDeadline && certificateDeadline < now;
                        
                        return (
                          <div className={`flex items-center p-3 border rounded-lg ${
                            isOverdue ? 'bg-secondary-100 border-secondary-300' : 'bg-secondary-50 border-secondary-200'
                          }`}>
                            <AlertCircle className={`h-5 w-5 mr-3 ${
                              isOverdue ? 'text-secondary-700' : 'text-secondary-600'
                            }`} />
                            <div className="flex-1">
                              <p className={`text-sm font-medium ${
                                isOverdue ? 'text-secondary-900' : 'text-secondary-800'
                              }`}>
                                {isOverdue ? 'Certificate submission overdue' : 'Certificate submission pending'}
                              </p>
                              <p className={`text-xs mt-1 ${
                                isOverdue ? 'text-secondary-700' : 'text-secondary-600'
                              }`}>
                                {isOverdue 
                                  ? `Overdue by ${Math.abs(daysLeft)} day${Math.abs(daysLeft) > 1 ? 's' : ''}`
                                  : daysLeft !== null 
                                    ? `${daysLeft} day${daysLeft !== 1 ? 's' : ''} remaining`
                                    : 'Deadline not set'
                                }
                              </p>
                            </div>
                            <Link
                              to="/student/proofs"
                              className="text-xs font-medium text-primary-600 hover:text-primary-800"
                            >
                              Submit Now
                            </Link>
                          </div>
                        );
                      } else {
                        const attendanceDeadline = deadlines.attendance_proof_deadline ? new Date(deadlines.attendance_proof_deadline) : null;
                        const daysLeft = attendanceDeadline ? differenceInDays(attendanceDeadline, now) : null;
                        const isOverdue = attendanceDeadline && attendanceDeadline < now;
                        
                        return (
                          <div className={`flex items-center p-3 border rounded-lg ${
                            isOverdue ? 'bg-secondary-100 border-secondary-300' : 'bg-secondary-50 border-secondary-200'
                          }`}>
                            <AlertCircle className={`h-5 w-5 mr-3 ${
                              isOverdue ? 'text-secondary-700' : 'text-secondary-600'
                            }`} />
                            <div className="flex-1">
                              <p className={`text-sm font-medium ${
                                isOverdue ? 'text-secondary-900' : 'text-secondary-800'
                              }`}>
                                {isOverdue ? 'Attendance proof overdue' : 'Attendance proof required'}
                              </p>
                              <p className={`text-xs mt-1 ${
                                isOverdue ? 'text-secondary-700' : 'text-secondary-600'
                              }`}>
                                {isOverdue 
                                  ? `Overdue by ${Math.abs(daysLeft)} day${Math.abs(daysLeft) > 1 ? 's' : ''}`
                                  : daysLeft !== null 
                                    ? `${daysLeft} day${daysLeft !== 1 ? 's' : ''} remaining`
                                    : 'Submit within 3 days of approval'
                                }
                              </p>
                            </div>
                            <Link
                              to="/student/proofs"
                              className="text-xs font-medium text-primary-600 hover:text-primary-800"
                            >
                              Submit Now
                            </Link>
                          </div>
                        );
                      }
                    })()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;