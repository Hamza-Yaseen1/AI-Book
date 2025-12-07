import type { ReactNode } from 'react';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './about.module.css';

export default function About(): ReactNode {
    return (
        <Layout
            title="About"
            description="Learn more about Physical AI Book - Your comprehensive guide to Physical AI">
            <div className={styles.aboutPage}>
                {/* Header Section */}
                <div className={styles.aboutHeader}>
                    <div className="container">
                        <Heading as="h1" className={styles.aboutTitle}>
                            About Physical AI Book
                        </Heading>
                        <p className={styles.aboutSubtitle}>
                            Your comprehensive guide to understanding and building Physical AI systems
                        </p>
                    </div>
                </div>

                {/* Content Sections */}
                <div className={styles.aboutContent}>
                    {/* Mission Section */}
                    <section className={styles.section}>
                        <Heading as="h2" className={styles.sectionTitle}>
                            Our Mission
                        </Heading>
                        <div className={styles.sectionContent}>
                            <p>
                                Physical AI Book is dedicated to bridging the gap between artificial intelligence
                                and the physical world. We believe that the future of AI lies not just in digital
                                spaces, but in systems that can perceive, understand, and interact with the real world.
                            </p>
                            <p>
                                Our mission is to provide comprehensive, accessible education on Physical AI - from
                                fundamental concepts to advanced implementations. Whether you're a student, researcher,
                                or industry professional, we're here to guide your journey into this exciting field.
                            </p>
                        </div>
                    </section>

                    {/* What is Physical AI Section */}
                    <section className={styles.section}>
                        <Heading as="h2" className={styles.sectionTitle}>
                            What is Physical AI?
                        </Heading>
                        <div className={styles.sectionContent}>
                            <p>
                                Physical AI represents the convergence of artificial intelligence with robotics,
                                sensors, and actuators to create systems that can interact with and manipulate
                                the physical world. This includes:
                            </p>
                            <div className={styles.featureGrid}>
                                <div className={styles.featureCard}>
                                    <div className={styles.featureIcon}>🤖</div>
                                    <div className={styles.featureTitle}>Robotics</div>
                                    <div className={styles.featureDescription}>
                                        Intelligent robots that can navigate, manipulate objects, and perform complex tasks
                                    </div>
                                </div>
                                <div className={styles.featureCard}>
                                    <div className={styles.featureIcon}>👁️</div>
                                    <div className={styles.featureTitle}>Computer Vision</div>
                                    <div className={styles.featureDescription}>
                                        Systems that can see and understand the physical environment
                                    </div>
                                </div>
                                <div className={styles.featureCard}>
                                    <div className={styles.featureIcon}>🎯</div>
                                    <div className={styles.featureTitle}>Sensor Fusion</div>
                                    <div className={styles.featureDescription}>
                                        Combining multiple sensor inputs for comprehensive environmental awareness
                                    </div>
                                </div>
                                <div className={styles.featureCard}>
                                    <div className={styles.featureIcon}>⚡</div>
                                    <div className={styles.featureTitle}>Real-time Control</div>
                                    <div className={styles.featureDescription}>
                                        AI systems that can make split-second decisions and adjustments
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* What You'll Learn Section */}
                    <section className={styles.section}>
                        <Heading as="h2" className={styles.sectionTitle}>
                            What You'll Learn
                        </Heading>
                        <div className={styles.sectionContent}>
                            <p>
                                This comprehensive guide covers everything from foundational concepts to
                                advanced implementations:
                            </p>
                            <ul>
                                <li>Fundamentals of AI and machine learning applied to physical systems</li>
                                <li>Sensor technologies and data processing techniques</li>
                                <li>Computer vision and perception algorithms</li>
                                <li>Motion planning and control systems</li>
                                <li>Hardware integration and embedded AI</li>
                                <li>Real-world applications and case studies</li>
                                <li>Best practices for building robust Physical AI systems</li>
                            </ul>
                        </div>
                    </section>

                    {/* Get Started Section */}
                    <section className={styles.section}>
                        <Heading as="h2" className={styles.sectionTitle}>
                            Get Started
                        </Heading>
                        <div className={styles.sectionContent}>
                            <p>
                                Ready to dive into the world of Physical AI? Start with our introduction chapter
                                and progress through hands-on examples, practical projects, and in-depth explanations.
                            </p>
                            <p>
                                Join our community of learners, researchers, and practitioners who are shaping
                                the future of AI in the physical world.
                            </p>
                        </div>
                    </section>
                </div>
            </div>
        </Layout>
    );
}
