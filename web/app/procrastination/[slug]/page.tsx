import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ProblemMicroTool } from "../../../components/problem-micro-tool";
import styles from "../../../components/problem-page.module.css";
import {
  getPublishedProblemPage,
  problemPagePath,
  publishedProblemPages,
} from "../../../content/problem-pages";
import { absoluteUrl } from "../../../lib/seo/site";

export const dynamicParams = false;

export function generateStaticParams() {
  return publishedProblemPages.map((page) => ({ slug: page.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const problem = getPublishedProblemPage(slug);
  if (!problem) return {};

  const canonical = absoluteUrl(problemPagePath(problem));

  return {
    title: problem.seoTitle,
    description: problem.seoDescription,
    alternates: {
      canonical,
    },
    robots: {
      index: true,
      follow: true,
    },
    openGraph: {
      type: "website",
      siteName: "Вместе к цели",
      locale: "ru_RU",
      url: canonical,
      title: problem.seoTitle,
      description: problem.seoDescription,
    },
  };
}

export default async function ProblemPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const problem = getPublishedProblemPage(slug);
  if (!problem) notFound();

  const related = (problem.relatedSlugs ?? [])
    .map((relatedSlug) => getPublishedProblemPage(relatedSlug))
    .filter((page): page is NonNullable<typeof page> => Boolean(page));

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <header className={styles.topbar}>
          <Link className={styles.brand} href="/">
            Вместе к цели
          </Link>
          <Link className={styles.backLink} href="/">
            О проекте
          </Link>
        </header>

        <section className={styles.hero}>
          <div className={styles.copy}>
            <p className={styles.eyebrow}>Практический инструмент</p>
            <h1>{problem.title}</h1>
            <p className={styles.intro}>{problem.intro}</p>
            <div className={styles.freeNote} aria-label="Условия использования">
              <span>Без регистрации</span>
              <span>Первый результат сразу</span>
              <span>Личный текст не публикуется</span>
            </div>
          </div>

          <ProblemMicroTool problem={problem} />
        </section>

        <section className={styles.context} aria-labelledby="how-it-works">
          <h2 id="how-it-works">Здесь не нужен большой план</h2>
          <p>
            Сначала инструмент помогает получить одно выполнимое действие.
            Затем его можно уменьшить ещё сильнее или попросить следующий шаг.
            Только после этого появляется предложение сохранить результат в
            основном рабочем пространстве «Вместе к цели».
          </p>
        </section>

        {related.length ? (
          <nav className={styles.related} aria-label="Похожие ситуации">
            <h2>Похожие ситуации</h2>
            <div className={styles.relatedGrid}>
              {related.map((item) => (
                <Link
                  className={styles.relatedLink}
                  href={problemPagePath(item)}
                  key={item.slug}
                >
                  {item.title}
                </Link>
              ))}
            </div>
          </nav>
        ) : null}
      </div>
    </main>
  );
}
