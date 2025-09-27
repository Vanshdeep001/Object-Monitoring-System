// HeroSection.jsx
import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';
import VideoStream from '../VideoStream';
import ControlPanel from '../ControlPanel';
import StatisticsPanel from '../StatisticsPanel';
import ZoneManagement from '../ZoneManagement';
import { MonitoringType } from '../../types';
import { cn } from '../../lib/utils';
import LetterGlitch from '../LetterGlitch';
import StarBorder from '../StarBorder';
import TextPressure from '../TextPressure';

gsap.registerPlugin(ScrollTrigger);

interface HorizonHeroSectionProps {
  activeMonitoring: MonitoringType | null;
  isConnected: boolean;
  statistics: any;
  zones: any[];
  onStartMonitoring: (type: MonitoringType) => void;
  onStopMonitoring: () => void;
  onZonesChange: (newZones: any[]) => void;
  onMonitoringChange: (type: MonitoringType | null) => void;
}

export const HorizonHeroSection: React.FC<HorizonHeroSectionProps> = ({
  activeMonitoring,
  isConnected,
  statistics,
  zones,
  onStartMonitoring,
  onStopMonitoring,
  onZonesChange,
  onMonitoringChange,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLDivElement>(null);
  const scrollProgressRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);

  const smoothCameraPos = useRef({ x: 0, y: 30, z: 100 });
  
  const [scrollProgress, setScrollProgress] = useState(0);
  const [currentSection, setCurrentSection] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showMonitorMenu, setShowMonitorMenu] = useState(false);
  const [currentPage, setCurrentPage] = useState('landing'); // 'landing', 'monitor-menu', 'object-detection', 'zone-monitoring'
  const totalSections = 2;
  
  const threeRefs = useRef<{
    scene: THREE.Scene | null;
    camera: THREE.PerspectiveCamera | null;
    renderer: THREE.WebGLRenderer | null;
    composer: EffectComposer | null;
    stars: THREE.Points[];
    nebula: THREE.Mesh | null;
    mountains: THREE.Mesh[];
    animationId: number | null;
    targetCameraX?: number;
    targetCameraY?: number;
    targetCameraZ?: number;
    locations?: number[];
  }>({
    scene: null,
    camera: null,
    renderer: null,
    composer: null,
    stars: [],
    nebula: null,
    mountains: [],
    animationId: null
  });

  // Initialize Three.js
  useEffect(() => {
    const initThree = () => {
      const { current: refs } = threeRefs;
      
      // Scene setup
      refs.scene = new THREE.Scene();
      refs.scene.fog = new THREE.FogExp2(0x000000, 0.00025);

      // Camera
      refs.camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        2000
      );
      refs.camera.position.z = 100;
      refs.camera.position.y = 20;

      // Renderer
      refs.renderer = new THREE.WebGLRenderer({
        canvas: canvasRef.current || undefined,
        antialias: true,
        alpha: true
      });
      refs.renderer.setSize(window.innerWidth, window.innerHeight);
      refs.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      refs.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      refs.renderer.toneMappingExposure = 0.5;

      // Post-processing
      refs.composer = new EffectComposer(refs.renderer);
      const renderPass = new RenderPass(refs.scene, refs.camera);
      refs.composer.addPass(renderPass);

      const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        0.8,
        0.4,
        0.85
      );
      refs.composer.addPass(bloomPass);

      // Create scene elements
      createStarField();
      createNebula();
      createMountains();
      createAtmosphere();
      getLocation();

      // Start animation
      animate();
      
      // Mark as ready after Three.js is initialized
      setIsReady(true);
    };

    const createStarField = () => {
      const { current: refs } = threeRefs;
      const starCount = 5000;
      
      for (let i = 0; i < 3; i++) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(starCount * 3);
        const colors = new Float32Array(starCount * 3);
        const sizes = new Float32Array(starCount);

        for (let j = 0; j < starCount; j++) {
          const radius = 200 + Math.random() * 800;
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.acos(Math.random() * 2 - 1);

          positions[j * 3] = radius * Math.sin(phi) * Math.cos(theta);
          positions[j * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
          positions[j * 3 + 2] = radius * Math.cos(phi);

          // Color variation
          const color = new THREE.Color();
          const colorChoice = Math.random();
          if (colorChoice < 0.7) {
            color.setHSL(0, 0, 0.8 + Math.random() * 0.2);
          } else if (colorChoice < 0.9) {
            color.setHSL(0.08, 0.5, 0.8);
          } else {
            color.setHSL(0.6, 0.5, 0.8);
          }
          
          colors[j * 3] = color.r;
          colors[j * 3 + 1] = color.g;
          colors[j * 3 + 2] = color.b;

          sizes[j] = Math.random() * 2 + 0.5;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

        const material = new THREE.ShaderMaterial({
          uniforms: {
            time: { value: 0 },
            depth: { value: i }
          },
          vertexShader: `
            attribute float size;
            attribute vec3 color;
            varying vec3 vColor;
            uniform float time;
            uniform float depth;
            
            void main() {
              vColor = color;
              vec3 pos = position;
              
              // Slow rotation based on depth
              float angle = time * 0.05 * (1.0 - depth * 0.3);
              mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
              pos.xy = rot * pos.xy;
              
              vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
              gl_PointSize = size * (300.0 / -mvPosition.z);
              gl_Position = projectionMatrix * mvPosition;
            }
          `,
          fragmentShader: `
            varying vec3 vColor;
            
            void main() {
              float dist = length(gl_PointCoord - vec2(0.5));
              if (dist > 0.5) discard;
              
              float opacity = 1.0 - smoothstep(0.0, 0.5, dist);
              gl_FragColor = vec4(vColor, opacity);
            }
          `,
          transparent: true,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        });

        const stars = new THREE.Points(geometry, material);
        refs.scene!.add(stars);
        refs.stars.push(stars);
      }
    };

    const createNebula = () => {
      const { current: refs } = threeRefs;
      
      const geometry = new THREE.PlaneGeometry(8000, 4000, 100, 100);
      const material = new THREE.ShaderMaterial({
        uniforms: {
          time: { value: 0 },
          color1: { value: new THREE.Color(0x0033ff) },
          color2: { value: new THREE.Color(0xff0066) },
          opacity: { value: 0.3 }
        },
        vertexShader: `
          varying vec2 vUv;
          varying float vElevation;
          uniform float time;
          
          void main() {
            vUv = uv;
            vec3 pos = position;
            
            float elevation = sin(pos.x * 0.01 + time) * cos(pos.y * 0.01 + time) * 20.0;
            pos.z += elevation;
            vElevation = elevation;
            
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 color1;
          uniform vec3 color2;
          uniform float opacity;
          uniform float time;
          varying vec2 vUv;
          varying float vElevation;
          
          void main() {
            float mixFactor = sin(vUv.x * 10.0 + time) * cos(vUv.y * 10.0 + time);
            vec3 color = mix(color1, color2, mixFactor * 0.5 + 0.5);
            
            float alpha = opacity * (1.0 - length(vUv - 0.5) * 2.0);
            alpha *= 1.0 + vElevation * 0.01;
            
            gl_FragColor = vec4(color, alpha);
          }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
        depthWrite: false
      });

      const nebula = new THREE.Mesh(geometry, material);
      nebula.position.z = -1050;
      nebula.rotation.x = 0;
      refs.scene!.add(nebula);
      refs.nebula = nebula;
    };

    const createMountains = () => {
      const { current: refs } = threeRefs;
      
      const layers = [
        { distance: -50, height: 60, color: 0x1a1a2e, opacity: 1 },
        { distance: -100, height: 80, color: 0x16213e, opacity: 0.8 },
        { distance: -150, height: 100, color: 0x0f3460, opacity: 0.6 },
        { distance: -200, height: 120, color: 0x0a4668, opacity: 0.4 }
      ];

      layers.forEach((layer, index) => {
        const points = [];
        const segments = 50;
        
        for (let i = 0; i <= segments; i++) {
          const x = (i / segments - 0.5) * 1000;
          const y = Math.sin(i * 0.1) * layer.height + 
                   Math.sin(i * 0.05) * layer.height * 0.5 +
                   Math.random() * layer.height * 0.2 - 100;
          points.push(new THREE.Vector2(x, y));
        }
        
        points.push(new THREE.Vector2(5000, -300));
        points.push(new THREE.Vector2(-5000, -300));

        const shape = new THREE.Shape(points);
        const geometry = new THREE.ShapeGeometry(shape);
        const material = new THREE.MeshBasicMaterial({
          color: layer.color,
          transparent: true,
          opacity: layer.opacity,
          side: THREE.DoubleSide
        });

        const mountain = new THREE.Mesh(geometry, material);
        mountain.position.z = layer.distance;
        mountain.position.y = layer.distance;
        mountain.userData = { baseZ: layer.distance, index };
        refs.scene!.add(mountain);
        refs.mountains.push(mountain);
      });
    };

    const createAtmosphere = () => {
      const { current: refs } = threeRefs;
      
      const geometry = new THREE.SphereGeometry(600, 32, 32);
      const material = new THREE.ShaderMaterial({
        uniforms: {
          time: { value: 0 }
        },
        vertexShader: `
          varying vec3 vNormal;
          varying vec3 vPosition;
          
          void main() {
            vNormal = normalize(normalMatrix * normal);
            vPosition = position;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          varying vec3 vNormal;
          varying vec3 vPosition;
          uniform float time;
          
          void main() {
            float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
            vec3 atmosphere = vec3(0.3, 0.6, 1.0) * intensity;
            
            float pulse = sin(time * 2.0) * 0.1 + 0.9;
            atmosphere *= pulse;
            
            gl_FragColor = vec4(atmosphere, intensity * 0.25);
          }
        `,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        transparent: true
      });

      const atmosphere = new THREE.Mesh(geometry, material);
      refs.scene!.add(atmosphere);
    };

    const animate = () => {
      const { current: refs } = threeRefs;
      refs.animationId = requestAnimationFrame(animate);
      
      const time = Date.now() * 0.001;

      // Update stars
      refs.stars.forEach((starField, i) => {
        const material = starField.material as THREE.ShaderMaterial;
        if (material.uniforms) {
          material.uniforms.time.value = time;
        }
      });

      // Update nebula
      if (refs.nebula) {
        const material = refs.nebula.material as THREE.ShaderMaterial;
        if (material.uniforms) {
          material.uniforms.time.value = time * 0.5;
        }
      }

      // Smooth camera movement with easing
      if (refs.camera && refs.targetCameraX !== undefined && refs.targetCameraY !== undefined && refs.targetCameraZ !== undefined) {
        const smoothingFactor = 0.05;
        
        smoothCameraPos.current.x += (refs.targetCameraX - smoothCameraPos.current.x) * smoothingFactor;
        smoothCameraPos.current.y += (refs.targetCameraY - smoothCameraPos.current.y) * smoothingFactor;
        smoothCameraPos.current.z += (refs.targetCameraZ - smoothCameraPos.current.z) * smoothingFactor;
        
        const floatX = Math.sin(time * 0.1) * 2;
        const floatY = Math.cos(time * 0.15) * 1;
        
        refs.camera.position.x = smoothCameraPos.current.x + floatX;
        refs.camera.position.y = smoothCameraPos.current.y + floatY;
        refs.camera.position.z = smoothCameraPos.current.z;
        refs.camera.lookAt(0, 10, -600);
      }

      // Parallax mountains with subtle animation
      refs.mountains.forEach((mountain, i) => {
        const parallaxFactor = 1 + i * 0.5;
        mountain.position.x = Math.sin(time * 0.1) * 2 * parallaxFactor;
        mountain.position.y = 50 + (Math.cos(time * 0.15) * 1 * parallaxFactor);
      });

      if (refs.composer) {
        refs.composer.render();
      }
    };

    initThree();

    // Handle resize
    const handleResize = () => {
      const { current: refs } = threeRefs;
      if (refs.camera && refs.renderer && refs.composer) {
        refs.camera.aspect = window.innerWidth / window.innerHeight;
        refs.camera.updateProjectionMatrix();
        refs.renderer.setSize(window.innerWidth, window.innerHeight);
        refs.composer.setSize(window.innerWidth, window.innerHeight);
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      const { current: refs } = threeRefs;
      
      if (refs.animationId) {
        cancelAnimationFrame(refs.animationId);
      }

      window.removeEventListener('resize', handleResize);

      // Dispose Three.js resources
      refs.stars.forEach(starField => {
        starField.geometry.dispose();
        const material = starField.material as THREE.Material;
        material.dispose();
      });

      refs.mountains.forEach(mountain => {
        mountain.geometry.dispose();
        const material = mountain.material as THREE.Material;
        material.dispose();
      });

      if (refs.nebula) {
        refs.nebula.geometry.dispose();
        const material = refs.nebula.material as THREE.Material;
        material.dispose();
      }

      if (refs.renderer) {
        refs.renderer.dispose();
      }
    };
  }, []);

  const getLocation = () => {
    const { current: refs } = threeRefs;
    const locations: number[] = [];
    refs.mountains.forEach((mountain, i) => {
      locations[i] = mountain.position.z;
    });
    refs.locations = locations;
  };

  // GSAP Animations - Run after component is ready
  useEffect(() => {
    if (!isReady) return;
    
    gsap.set([menuRef.current, titleRef.current, subtitleRef.current, scrollProgressRef.current], {
      visibility: 'visible'
    });

    const tl = gsap.timeline();

    // Animate menu
    if (menuRef.current) {
      gsap.set(menuRef.current, {
        x: 0,
        opacity: 1,
        visibility: 'visible'
      });
      tl.from(menuRef.current, {
        x: -100,
        opacity: 0,
        duration: 1,
        ease: "power3.out"
      });
    }

    // Animate title lines
    if (titleRef.current) {
      const titleLines = titleRef.current.querySelectorAll('.title-line');
      tl.from(titleLines, {
        y: 200,
        opacity: 0,
        duration: 1.5,
        stagger: 0.2,
        ease: "power4.out"
      }, "-=0.5");
    }

    // Animate subtitle lines
    if (subtitleRef.current) {
      const subtitleLines = subtitleRef.current.querySelectorAll('.subtitle-line');
      tl.from(subtitleLines, {
        y: 50,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: "power3.out"
      }, "-=0.8");
    }

    // Animate scroll indicator
    if (scrollProgressRef.current) {
      tl.from(scrollProgressRef.current, {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: "power2.out"
      }, "-=0.5");
    }

    // Disabled scroll-triggered animations to prevent text collapsing
    // if (titleRef.current && subtitleRef.current) {
    //   gsap.to([titleRef.current, subtitleRef.current], {
    //     y: -window.innerHeight * 0.6,
    //     opacity: 0,
    //     duration: 1,
    //     ease: "power2.inOut",
    //     scrollTrigger: {
    //       trigger: containerRef.current,
    //       start: "top top",
    //       end: "50% top",
    //       scrub: 1,
    //     }
    //   });
    // }

    // Animate canvas movement
    if (canvasRef.current) {
      gsap.to(canvasRef.current, {
        y: -window.innerHeight * 0.2,
        scale: 0.9,
        duration: 1,
        ease: "power2.inOut",
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: "50% top",
          scrub: 1,
        }
      });
    }

    return () => {
      tl.kill();
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, [isReady]);

  // Scroll handling
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const maxScroll = documentHeight - windowHeight;
      const progress = Math.min(scrollY / maxScroll, 1);
      
      setScrollProgress(progress);
      const newSection = Math.floor(progress * totalSections);
      setCurrentSection(newSection);

      // Show dashboard when scrolled past 50%
      setShowDashboard(progress > 0.5);

      const { current: refs } = threeRefs;
      
      // Calculate smooth progress through all sections
      const totalProgress = progress * totalSections;
      const sectionProgress = totalProgress % 1;
      
      // Define camera positions for each section
      const cameraPositions = [
        { x: 0, y: 30, z: 300 },
        { x: 0, y: 40, z: -50 },
        { x: 0, y: 50, z: -700 }
      ];
      
      // Get current and next positions
      const currentPos = cameraPositions[newSection] || cameraPositions[0];
      const nextPos = cameraPositions[newSection + 1] || currentPos;
      
      // Set target positions
      refs.targetCameraX = currentPos.x + (nextPos.x - currentPos.x) * sectionProgress;
      refs.targetCameraY = currentPos.y + (nextPos.y - currentPos.y) * sectionProgress;
      refs.targetCameraZ = currentPos.z + (nextPos.z - currentPos.z) * sectionProgress;
      
      // Smooth parallax for mountains
      refs.mountains.forEach((mountain, i) => {
        const speed = 1 + i * 0.9;
        const targetZ = mountain.userData.baseZ + scrollY * speed * 0.5;
        refs.nebula!.position.z = (targetZ + progress * speed * 0.01) - 100;
        
        mountain.userData.targetZ = targetZ;
        if (progress > 0.7) {
          mountain.position.z = 600000;
        }
        if (progress < 0.7) {
          if (refs.locations) {
            mountain.position.z = refs.locations[i];
          }
        }
      });
      refs.nebula!.position.z = refs.mountains[3].position.z;
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll();
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [totalSections]);

  const splitTitle = (text: string) => {
    return text.split('').map((char, i) => (
      <span key={i} className="title-char">
        {char}
      </span>
    ));
  };

  return (
    <div ref={containerRef} className="hero-container cosmos-style">
      <canvas ref={canvasRef} className="hero-canvas" />
      
      {/* Side menu */}
      <div ref={menuRef} className="side-menu" style={{ visibility: 'visible' }}>
        <div className="menu-icon" onClick={() => setShowMonitorMenu(true)}>
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div className="vertical-text" onClick={() => setShowMonitorMenu(true)}>MONITOR</div>
      </div>

      {/* Main content */}
      <div className="hero-content cosmos-content">
        {/* LetterGlitch Background for Landing Page */}
        <div className="landing-letterglitch-background">
          <LetterGlitch
            glitchColors={['#dc2626', '#991b1b', '#7f1d1d', '#ef4444', '#b91c1c', '#ff4757']}
            glitchSpeed={80}
            centerVignette={false}
            outerVignette={true}
            smooth={true}
            characters="OBJECTMONITORINGDASHBOARDABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$&*()-_+=/[]{};:<>.,"
          />
        </div>
        
        <h1 ref={titleRef} className="hero-title">
          <div className="title-line">OBJECT</div>
          <div className="title-line">MONITORING</div>
          <div className="title-line">DASHBOARD</div>
        </h1>
        
        <div ref={subtitleRef} className="hero-subtitle cosmos-subtitle">
          <p className="subtitle-line">
            Advanced AI-powered surveillance system
          </p>
          <p className="subtitle-line">
            Real-time object detection and zone monitoring
          </p>
        </div>
      </div>

      {/* Dashboard Overlay - Only visible when showDashboard is true */}
      {showDashboard && (
        <div ref={dashboardRef} className="dashboard-overlay">
          <div className="absolute top-4 right-4 z-30">
            <div className={cn(
              "status-indicator",
              isConnected ? "status-online" : "status-offline"
            )}>
              {isConnected ? '🟢 ONLINE' : '🔴 OFFLINE'}
            </div>
          </div>

          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4/5 h-3/4 z-20">
            <div className="grid grid-cols-12 grid-rows-6 gap-4 h-full">
              {/* Video Stream - Main Area */}
              <div className="col-span-8 row-span-4 futuristic-panel p-4">
                <VideoStream 
                  activeMonitoring={activeMonitoring}
                  onMonitoringChange={onMonitoringChange}
                />
              </div>

              {/* Control Panel */}
              <div className="col-span-4 row-span-2 futuristic-panel p-4">
                <ControlPanel
                  activeMonitoring={activeMonitoring}
                  onStart={onStartMonitoring}
                  onStop={onStopMonitoring}
                  isConnected={isConnected}
                />
              </div>

              {/* Statistics Panel */}
              <div className="col-span-4 row-span-2 futuristic-panel p-4">
                <StatisticsPanel
                  statistics={statistics}
                  activeMonitoring={activeMonitoring}
                />
              </div>

              {/* Zone Management */}
              <div className="col-span-8 row-span-2 futuristic-panel p-4">
                <ZoneManagement
                  zones={zones}
                  onZonesChange={onZonesChange}
                  isConnected={isConnected}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scroll progress indicator */}
      <div ref={scrollProgressRef} className="scroll-progress" style={{ visibility: 'hidden' }}>
        <div className="scroll-text">SCROLL</div>
        <div className="progress-track">
          <div 
            className="progress-fill" 
            style={{ width: `${scrollProgress * 100}%` }}
          />
        </div>
        <div className="section-counter">
          {String(currentSection + 1).padStart(2, '0')} / {String(totalSections).padStart(2, '0')}
        </div>
      </div>

      {/* Monitor Menu Overlay */}
      {showMonitorMenu && (
        <div className="monitor-menu-overlay">
          {/* LetterGlitch Background */}
          <div className="letterglitch-background">
            <LetterGlitch
              glitchColors={['#dc2626', '#991b1b', '#7f1d1d', '#ef4444', '#b91c1c']}
              glitchSpeed={100}
              centerVignette={true}
              outerVignette={false}
              smooth={true}
              characters="OBJECTDETECTIONZONEMONITORINGABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$&*()-_+=/[]{};:<>.,"
            />
          </div>
          
          <div className="monitor-menu-content">
            <div className="monitor-menu-header">
              <h2 className="monitor-menu-title">SELECT MONITORING TYPE</h2>
              <button 
                className="close-button"
                onClick={() => setShowMonitorMenu(false)}
              >
                ×
              </button>
            </div>
            
            <div className="monitor-options">
              <div 
                className="monitor-option object-detection-option"
                onClick={() => {
                  setCurrentPage('object-detection');
                  setShowMonitorMenu(false);
                }}
              >
                <div className="option-icon">
                  <div className="icon-circle">
                    <div className="icon-target"></div>
                  </div>
                </div>
                <div className="option-title">OBJECT DETECTION</div>
                <div className="option-description">Real-time object detection and tracking</div>
                <div className="option-overlay"></div>
              </div>
              
              <div 
                className="monitor-option zone-monitoring-option"
                onClick={() => {
                  setCurrentPage('zone-monitoring');
                  setShowMonitorMenu(false);
                }}
              >
                <div className="option-icon">
                  <div className="icon-circle">
                    <div className="icon-zone"></div>
                  </div>
                </div>
                <div className="option-title">ZONE MONITORING</div>
                <div className="option-description">Restricted area monitoring and alerts</div>
                <div className="option-overlay"></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Object Detection Page */}
      {currentPage === 'object-detection' && (
        <div className="monitoring-page">
          <div className="page-header">
            <StarBorder 
              as="button"
              className="back-button"
              color="#ff4757"
              speed="4s"
              onClick={() => setCurrentPage('landing')}
            >
              ← BACK
            </StarBorder>
            <div className="text-pressure-container">
              <TextPressure
                text="OBJECT DETECTION"
                textColor="#ff4757"
                strokeColor="#ff4757"
                stroke={true}
                strokeWidth={2}
                width={true}
                weight={true}
                italic={true}
                alpha={false}
                flex={false}
                scale={false}
                minFontSize={36}
                className="page-title-textpressure"
              />
            </div>
          </div>
          
          <div className="monitoring-content">
            <div className="video-container">
              <VideoStream 
                activeMonitoring={activeMonitoring}
                onMonitoringChange={onMonitoringChange}
              />
            </div>
            
            <div className="controls-panel">
              <div className="control-section">
                <h3>Detection Settings</h3>
                <div className="control-item">
                  <label>Confidence Threshold</label>
                  <input type="range" min="0.1" max="1" step="0.1" defaultValue="0.5" />
                </div>
                <div className="control-item">
                  <label>Detection Classes</label>
                  <select>
                    <option>All Classes</option>
                    <option>Person Only</option>
                    <option>Vehicles Only</option>
                  </select>
                </div>
              </div>
              
           <div className="control-section">
             <h3>Actions</h3>
             <StarBorder 
               className="action-button start" 
               color="#10b981" 
               speed="5s"
               onClick={async () => {
                 try {
                   const response = await fetch('http://localhost:8000/api/start/object-detection', {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' }
                   });
                   if (response.ok) {
                     const data = await response.json();
                     console.log('Object detection started:', data);
                     onStartMonitoring('object_detection');
                   }
                 } catch (error) {
                   console.error('Error starting object detection:', error);
                 }
               }}
             >
               START DETECTION
             </StarBorder>
             <StarBorder 
               className="action-button stop" 
               color="#ef4444" 
               speed="5s"
               onClick={async () => {
                 try {
                   const response = await fetch('http://localhost:8000/api/stop', {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' }
                   });
                   if (response.ok) {
                     const data = await response.json();
                     console.log('Monitoring stopped:', data);
                     onStopMonitoring();
                   }
                 } catch (error) {
                   console.error('Error stopping monitoring:', error);
                 }
               }}
             >
               STOP DETECTION
             </StarBorder>
             <StarBorder 
               className="action-button save" 
               color="#3b82f6" 
               speed="5s"
               onClick={() => {
                 // Save screenshot functionality
                 console.log('Saving screenshot...');
               }}
             >
               SAVE SCREENSHOT
             </StarBorder>
           </div>
            </div>
          </div>
        </div>
      )}

      {/* Zone Monitoring Page */}
      {currentPage === 'zone-monitoring' && (
        <div className="monitoring-page">
          <div className="page-header">
            <StarBorder 
              as="button"
              className="back-button"
              color="#ff4757"
              speed="4s"
              onClick={() => setCurrentPage('landing')}
            >
              ← BACK
            </StarBorder>
            <div className="text-pressure-container">
              <TextPressure
                text="ZONE MONITORING"
                textColor="#ff4757"
                strokeColor="#ff4757"
                stroke={true}
                strokeWidth={2}
                width={true}
                weight={true}
                italic={true}
                alpha={false}
                flex={false}
                scale={false}
                minFontSize={36}
                className="page-title-textpressure"
              />
            </div>
          </div>
          
          <div className="monitoring-content">
            <div className="video-container">
              <VideoStream 
                activeMonitoring={activeMonitoring}
                onMonitoringChange={onMonitoringChange}
              />
            </div>
            
            <div className="controls-panel">
              <div className="control-section">
                <h3>Zone Management</h3>
                <div className="control-item">
                  <StarBorder className="zone-button" color="#8b5cf6" speed="5s">
                    ADD RECTANGLE ZONE
                  </StarBorder>
                  <StarBorder className="zone-button" color="#8b5cf6" speed="5s">
                    ADD POLYGON ZONE
                  </StarBorder>
                  <StarBorder className="zone-button" color="#ef4444" speed="5s">
                    CLEAR ALL ZONES
                  </StarBorder>
                </div>
              </div>
              
              <div className="control-section">
                <h3>Alert Settings</h3>
                <div className="control-item">
                  <label>Alert Cooldown (seconds)</label>
                  <input type="number" min="1" max="60" defaultValue="2" />
                </div>
                <div className="control-item">
                  <label>Sound Alerts</label>
                  <input type="checkbox" defaultChecked />
                </div>
              </div>
              
              <div className="control-section">
                <h3>Actions</h3>
                <StarBorder 
                  className="action-button start" 
                  color="#10b981" 
                  speed="5s"
                  onClick={async () => {
                    try {
                      const response = await fetch('http://localhost:8000/api/start/zone-monitoring', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                      });
                      if (response.ok) {
                        const data = await response.json();
                        console.log('Zone monitoring started:', data);
                        onStartMonitoring('zone_monitoring');
                      }
                    } catch (error) {
                      console.error('Error starting zone monitoring:', error);
                    }
                  }}
                >
                  START MONITORING
                </StarBorder>
                <StarBorder 
                  className="action-button stop" 
                  color="#ef4444" 
                  speed="5s"
                  onClick={async () => {
                    try {
                      const response = await fetch('http://localhost:8000/api/stop', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                      });
                      if (response.ok) {
                        const data = await response.json();
                        console.log('Monitoring stopped:', data);
                        onStopMonitoring();
                      }
                    } catch (error) {
                      console.error('Error stopping monitoring:', error);
                    }
                  }}
                >
                  STOP MONITORING
                </StarBorder>
                <StarBorder 
                  className="action-button save" 
                  color="#3b82f6" 
                  speed="5s"
                  onClick={() => {
                    // Save zones functionality
                    console.log('Saving zones...');
                  }}
                >
                  SAVE ZONES
                </StarBorder>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Additional sections for scrolling - removed to prevent overlapping */}
      <div className="scroll-sections">
        {/* Removed duplicate DASHBOARD and ANALYTICS sections to prevent text overlapping */}
      </div>
    </div>
  );
};